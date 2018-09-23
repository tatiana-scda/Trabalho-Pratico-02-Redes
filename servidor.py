#!/usr/bin/env python3

import socket
import hashlib
import time
import bitstring
import sys
import threading
import struct

arquivo_saida  = sys.argv[1]
port           = sys.argv[2]
tamanho_janela = sys.argv[3]
md5_erro       = sys.argv[5]

janelaDeslizantePacotes = {}
janelaDeslizante = {}
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
    return pacote

def criadorPacoteACK(num_seq, timestamp_seg, timestamp_nanoseg):
    pacote                      = bytearray([])
    pacote.extend(num_seq)
    pacote.extend(timestamp_seg)
    pacote.extend(timestamp_nanoseg)
    pacote                      = calculaMD5ACK(pacote)
    print(pacote)
    return pacote

def processaPacote(pacote):
    ack = criadorPacoteACK(pacote[0:8], pacote[8:16],pacote[16:20])
    tcp.send(ack)

    with open(arquivo_saida, 'r') as saida:
        print saida.read()


def recebendoPacote(pacote):#ACK
        pacote            = tcp.recv(22)
        tamanho = int.from_bytes(pacote[20:22], byteorder='big', signed=False) 
        pacote.extend(tcp.recv(tamanho+16))

        if(calculaMD5Pacote(pacote)): #se o md5 funcionar para o pacote
            
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            if seqNum in range(primeiro_janela, primeiro_janela + tamanho_janela):
                janelaDeslizantePacotes[seqNum] = pacote
                if seqNum != primeiro_janela:
                    completo = True
                    for i in range(primeiro_janela, seqNum):
                    if janelaDeslizantePacotes[i]== "":
                        completo = False
                    if completo:
                        processaPacote(pacote)
                processaPacote(pacote)

threading.Thread(target = recebendoPacoteACK, args = (tcp, )).start()
threading.Thread(target = processarArquivo,   args = (tcp, )).start()

