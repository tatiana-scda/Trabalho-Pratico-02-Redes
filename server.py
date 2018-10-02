#!/usr/bin/env python3

import random
import socket
import hashlib
import time
import bitstring
import sys
from threading import Timer
from threading import Lock
from collections import defaultdict

arquivo_saida  = sys.argv[1]
port           = sys.argv[2]
tamanho_janela = int(sys.argv[3])
md5_erro       = float(sys.argv[4])
saida          = open(arquivo_saida, 'w')

janela                       = {}   
janela_lock                  = Lock()
janela_cliente               = {}

HOST = '127.0.0.1'
PORT = int(port)

dest = (HOST, PORT)

udp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udp.bind(dest)

def calculaMD5Pacote(pacote): 
    size                           = int.from_bytes(pacote[20:22], byteorder='big', signed=False) 
    m                              = hashlib.md5()
    m.update(pacote[0:22+size])
    md5                            = m.digest()
    return pacote[22+size:38+size] == md5

def calculaMD5ACK(pacote):
    global md5_erro
    m             = hashlib.md5()
    m.update(pacote[0:20])
    md5           = m.digest()
    pacote[20:36] = md5

    rand                 = random.random()
    if rand < md5_erro:
        pacote[35:36]    = bitstring.BitArray(uint=0, length=8).bytes
    return pacote

def criadorPacoteACK(seq_num):
    timestamp         = time.time() #para o seg e nanoseg serem da mesma base
    timestamp_sec     = bitstring.BitArray(uint=int(timestamp), length=64).bytes
    timestamp_nanosec = bitstring.BitArray(uint=int((timestamp % 1)*(10 ** 9)), length=32).bytes
    seq_num           = bitstring.BitArray(uint=int(seq_num), length=64).bytes

    pacote            = bytearray([])
    pacote.extend(seq_num)
    pacote.extend(timestamp_sec)
    pacote.extend(timestamp_nanosec)
    pacote.extend(calculaMD5ACK(pacote))
    return pacote

def processaPacote(pacote, tamanho):
    mensagem = pacote[22:22+tamanho]
    saida.write(mensagem.decode("UTF-8") + "\n")
    saida.flush()

def recebendoPacote(): #ACK
    global janela_cliente, dest, udp
    
    pacoteb, cliente = udp.recvfrom(65535+38)
    endereco_cliente = cliente[0]+':'+str(cliente[1])

    if(endereco_cliente not in janela_cliente):
        #inicio da janela, tamanho da janela, dict para janela delizante
        janela_cliente[endereco_cliente] = [1, tamanho_janela, {}]

    tamanho  = int.from_bytes(pacoteb[20:22], byteorder='big', signed=False) 
    pacote   = bytearray(pacoteb)

    if(calculaMD5Pacote(pacote)): #se o md5 funcionar para o pacote

        seq_num       = pacote[0:8]
        seq_num       = int.from_bytes(seq_num, byteorder='big', signed=False) #transformar de bytearray para int
        fim_janela    = janela_cliente[endereco_cliente][1]
        inicio_janela = janela_cliente[endereco_cliente][0]

        #print('Recebeu pacote OK', seq_num, inicio_janela, fim_janela)

        #se o pacpte estiver fora da janela
        if (seq_num > fim_janela):
            return

        if (seq_num >= inicio_janela):
            timestamp_sec     = int.from_bytes(pacote[8:16], byteorder='big', signed=False)
            timestamp_nanosec = int.from_bytes(pacote[16:20], byteorder='big', signed=False)

            janela_cliente[endereco_cliente][2][seq_num] = {'msg': pacote[22:22+tamanho], 'sec': timestamp_sec, 'nsec': timestamp_nanosec}

            if (seq_num == inicio_janela):
                i = seq_num
                while i in janela_cliente[endereco_cliente][2]:
                    del janela_cliente[endereco_cliente][2][i]
                    janela_cliente[endereco_cliente][0] += 1
                    janela_cliente[endereco_cliente][1] += 1
                    i += 1
            
            processaPacote(pacote, tamanho)
            
        ack = criadorPacoteACK(seq_num)
        udp.sendto(ack, cliente)

while True:
    recebendoPacote()
