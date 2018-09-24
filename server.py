#!/usr/bin/env python3

import random
import socket
import hashlib
import time
import bitstring
import sys
import threading
import struct

arquivo_saida  = sys.argv[1]
port           = sys.argv[2]
tamanho_janela = int(sys.argv[3])
md5_erro       = float(sys.argv[4])

HOST = '127.0.0.1'
PORT = int(port)

dest = (HOST, PORT)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udp.bind(dest)

def calculaMD5Pacote(pacote):
    size = int.from_bytes(pacote[20:22], byteorder='big', signed=False) 
    m    = hashlib.md5()
    md5  = m.update(pacote[0:22+size])
    md5  = m.digest()
    return pacote[22+size:38+size] == md5

def calculaMD5ACK(pacote):
    m             = hashlib.md5()
    md5           = m.update(pacote)
    md5           = m.digest()
    pacote[20:36] = md5
    if random.random() > md5_erro:
        pacote[35:36] = bitstring.BitArray(uint=0, length=8).bytes
    return pacote

def criadorPacoteACK(num_seq, timestamp_seg, timestamp_nanoseg):
    pacote                      = bytearray([])
    pacote.extend(num_seq)
    pacote.extend(timestamp_seg)
    pacote.extend(timestamp_nanoseg)
    pacote                      = calculaMD5ACK(pacote)
    return pacote

def processaPacote(pacote, tamanho):
    ack = criadorPacoteACK(pacote[0:8], pacote[8:16],pacote[16:20])
    udp.sendto(ack, (dest))
    mensagem = pacote[22:22+tamanho]
    with open(arquivo_saida, 'w') as saida:
        import pdb; pdb.set_trace()
        saida.write(mensagem.decode("UTF-8"))
        saida.flush()

def recebendoPacote():#ACK
        pacoteb, cliente = udp.recvfrom(65535+38)

        tamanho = int.from_bytes(pacoteb[20:22], byteorder='big', signed=False) 
        pacote = bytearray(pacoteb)
        print(pacote)
        if(calculaMD5Pacote(pacote)): #se o md5 funcionar para o pacote
            
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            print(seqNum)
            print(pacote[22:22+tamanho])
            # if seqNum in range(primeiro_janela, primeiro_janela + tamanho_janela):
            #     janelaDeslizantePacotes[str(seqNum)] = pacote
            #     if seqNum != primeiro_janela:
            #         completo = True
            #         for i in range(primeiro_janela, seqNum):
            #             if (janelaDeslizantePacotes[str(i)]== ""):
            #                 completo = False
            #             if completo:
            #                 processaPacote(pacote, tamanho)
            #     processaPacote(pacote, tamanho)

while True:
    recebendoPacote()