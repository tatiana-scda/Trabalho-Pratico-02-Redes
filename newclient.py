#!/usr/bin/env python3

import random
import socket
import hashlib
import time
import bitstring
import sys
import threading
from collections import defaultdict

arquivo_entrada = sys.argv[1]
ip_port         = sys.argv[2]
tamanho_janela  = int(sys.argv[3])
timeout         = int(sys.argv[4])
md5_erro        = float(sys.argv[5])
janela_vazia    = True

janelaDeslizanteTempos = defaultdict(dict)
janelaDeslizantePacotes = defaultdict(dict)
janelaDeslizanteRecebidos = defaultdict(dict)
primeiro_janela = 0

HOST = ip_port[0:ip_port.find(':')]
PORT = int(ip_port[ip_port.find(':')+1:])
tcp  = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dest = (HOST, PORT)
tcp.connect(dest) #cria conexao

def calculaMD5ACK(pacote):
    m   = hashlib.md5()
    md5 = m.update(pacote[0:20])
    md5 = m.digest()
    return pacote[20:36] == md5

def calculaMD5(pacote, comeco):
    m                        = hashlib.md5()
    md5                      = m.update(pacote)
    md5                      = m.digest()
    pacote[comeco:comeco+16] = md5
    if random.random() > md5_erro:
        pacote[comeco+15:comeco+16] = bitstring.BitArray(uint=0, length=8).bytes
    return pacote

def criadorPacote(num_seq, timestamp_seg, timestamp_nanoseg, mensagem):
    pacote        = bytearray([])
    pacote[0:8]   = bitstring.BitArray(uint=num_seq, length=64).bytes
    pacote[8:16]  = bitstring.BitArray(uint=timestamp_seg, length=64).bytes
    pacote[16:20] = bitstring.BitArray(uint=timestamp_nanoseg, length=32).bytes
    pacote[20:22] = bitstring.BitArray(uint=len(mensagem), length=16).bytes
    pacote.extend(map(ord, mensagem))
    pacote        = calculaMD5(pacote, 22+len(mensagem))
    print(pacote)
    return pacote

def janelaEstaCheia():
    global janelaDeslizanteTempos
    global janelaDeslizantePacotes
    global janelaDeslizanteRecebidos
    global janela_vazia
    if janela_vazia == True:
        return False
    if len(janelaDeslizanteTempos) == tamanho_janela:
        esta_enviado = True
        for chave, valor in janelaDeslizanteRecebidos.items():
            if valor != {}: 
                esta_enviado = False
        if esta_enviado:
            janelaDeslizanteTempos    = defaultdict(dict)
            janelaDeslizantePacotes   = defaultdict(dict)
            janelaDeslizanteRecebidos = defaultdict(dict)
            janela_vazia = True
        return True
    return False

def processarArquivo():
    global janela_vazia
    with open(arquivo_entrada) as file:
        id_pacote = 0
        tempo_passado = time.time() - timeout
        while True:
            for i in range(primeiro_janela, primeiro_janela + tamanho_janela):
                if janelaDeslizanteTempos[str(i)] != {}:
                    tempo = time.time() - janelaDeslizanteTempos[str(i)]
                    if tempo > timeout:
                        tcp.send(janelaDeslizantePacotes[str(i)])
                        janelaDeslizanteTempos[str(i)] = time.time()


            while not janelaEstaCheia(): #-1 pois tem de ter um espaco de buffer
                mensagem          = file.readline()
                
                timestamp         = time.time()
                timestamp_sec     = int(timestamp)
                timestamp_nanosec = int((timestamp % 1)*(10 ** 9))
                
                pacote            = criadorPacote(id_pacote, timestamp_sec, timestamp_nanosec, mensagem)
                tcp.send(pacote) #envia_pacote
                janelaDeslizantePacotes[str(id_pacote)] = pacote
                janelaDeslizanteTempos[str(id_pacote)]  = time.time()
                id_pacote                               = id_pacote+1
                janela_vazia = False


def recebendoPacoteACK():
        pacote = tcp.recv(36)
        if(calculaMD5ACK(pacote)): #se o md5 funcionar para o pacote
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            janelaDeslizanteRecebidos[str(seqNum)] = True

threading.Thread(target = recebendoPacoteACK).start()
threading.Thread(target = processarArquivo).start()
