#!/usr/bin/env python3

import socket
import hashlib
import time
import bitstring
import sys
import threading
import struct
from collections import defaultdict

arquivo_saida  = sys.argv[1]
port           = sys.argv[2]
tamanho_janela = int(sys.argv[3])
md5_erro       = float(sys.argv[4])

janelaDeslizantePacotes = defaultdict(dict) 
janelaDeslizante = defaultdict(dict)
primeiro_janela = 0

HOST = ''
PORT = int(port)
tcp  = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
origin = (HOST, PORT)
tcp.bind(origin)
tcp.listen(1) #cria conexao
tcp, adress = tcp.accept()

def calculaMD5Pacote(pacote):
    size = int.from_bytes(pacote[20:22]) 
    m    = hashlib.md5()
    md5  = m.update(pacote[0:22+size])
    md5  = m.digest()
    return pacote[22+size:38+size] == md5

def calculaMD5ACK(pacote):
    m             = hashlib.md5()
    md5           = m.update(pacote)
    md5           = m.digest()
    pacote[20:36] = md5
    if random.uniform(0,1) > md5_erro:
        pacote[36] = bitstring.BitArray(uint=0, lenght=4).bytes
    return pacote

def criadorPacoteACK(num_seq, timestamp_seg, timestamp_nanoseg):
    pacote                      = bytearray([])
    pacote.extend(num_seq)
    pacote.extend(timestamp_seg)
    pacote.extend(timestamp_nanoseg)
    pacote                      = calculaMD5ACK(pacote)
    print(pacote)
    return pacote

def processaPacote(pacote, tamanho):
    ack = criadorPacoteACK(pacote[0:8], pacote[8:16],pacote[16:20])
    tcp.send(ack)
    mensagem = str(pacote[22:22+tamanho])
    with open(arquivo_saida, 'r') as saida:
        print (saida.read())

def recebendoPacote():#ACK
        pacoteb = tcp.recv(22)
        tamanho = int.from_bytes(pacoteb[20:22], byteorder='big', signed=False) 
        pacotez = tcp.recv(tamanho+16)
        pacote  = bytearray(pacoteb).extend(pacotez)

        if(calculaMD5Pacote(pacote)): #se o md5 funcionar para o pacote
            
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            if seqNum in range(primeiro_janela, primeiro_janela + tamanho_janela):
                janelaDeslizantePacotes[str(seqNum)] = pacote
                if seqNum != primeiro_janela:
                    completo = True
                    for i in range(primeiro_janela, seqNum):
                        if (janelaDeslizantePacotes[str(i)]== ""):
                            completo = False
                        if completo:
                            processaPacote(pacote, tamanho)
                processaPacote(pacote, tamanho)

while True:
    recebendoPacote()
