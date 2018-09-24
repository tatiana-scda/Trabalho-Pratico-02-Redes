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

janelaLock = Lock()
arquivo_entrada             = sys.argv[1]
ip_port                     = sys.argv[2]
tamanho_janela              = int(sys.argv[3])
timeout                     = int(sys.argv[4])
md5_erro                    = float(sys.argv[5])

janela                      = {}  
fimJanela                   = 1
inicioJanela                = 1

HOST = ip_port[0:ip_port.find(':')]
PORT = int(ip_port[ip_port.find(':')+1:])
udp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)

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

    rand = random.random()
    if rand < md5_erro:
        print(md5_erro, rand)
        print('CORROMPE')
        pacote[comeco+15] = (pacote[comeco+15] + 1) % 256
    return pacote

def bateuTimer(seqNum):
    global timeout

    print("bateu timer ", seqNum)
    janelaLock.acquire()
    enviaPacote(seqNum)
    janela[seqNum]['timer'] = Timer(timeout, bateuTimer, [seqNum])
    janela[seqNum]['timer'].start()
    janelaLock.release()
    
def enviaPacote(seqNum):
    global dest, udp, janelaLock
    if seqNum not in janela:
        print('Aborting send! seqNum acked!!!!!!!!!!!!')
        return
    pacote = criadorPacote(seqNum, janela[seqNum]['sec'], janela[seqNum]['nsec'], janela[seqNum]['msg'])
    udp.sendto(pacote, dest)
    print("o pacote é", pacote)


def criadorPacote(num_seq, timestamp_seg, timestamp_nanoseg, mensagem):
    pacote        = bytearray([])
    pacote[0:8]   = bitstring.BitArray(uint=num_seq, length=64).bytes
    pacote[8:16]  = bitstring.BitArray(uint=timestamp_seg, length=64).bytes
    pacote[16:20] = bitstring.BitArray(uint=timestamp_nanoseg, length=32).bytes
    pacote[20:22] = bitstring.BitArray(uint=len(mensagem), length=16).bytes
    pacote.extend(map(ord, mensagem))
    pacote        = calculaMD5(pacote, 22+len(mensagem))
    return pacote

def recebeACK():
    global udp

    pacote = udp.recvfrom(36)[0]
    correto = calculaMD5ACK(pacote) #se o md5 funcionar para o pacote
    seqNum = pacote[0:8]
    seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #bytearray para int
    return (seqNum, correto)

# def enviarPacote(dest, pacote):
#     global udp, timeout, janelaCheia

#     while (janelaCheia < tamanho_janela):
#         #criacao do pacote
#         pacote            = criadorPacote(id_pacote, timestamp_sec, timestamp_nanosec, mensagem)
#         udp.sendto(pacote, dest) #envia_pacote

#         for i in range (len(arquivo_entrada)):
#             while janelaDeslizante[i] != True:
#                 recebendoPacote(janelaDeslizante, arquivo_entrada, udp, dest, timeout) #incrementa janela
#     # except Exception as e:
    #     if janelaDeslizante[i]:
    #     enviarPacote(udp, dest, timeout)


def janelaDeslizante():
    global tamanho_janela, udp, dest, timeout, fimJanela, inicioJanela, janelaLock
    seqNum = 1
    with open(arquivo_entrada, "r") as file:
        for mensagem in file:
            mensagem = mensagem.rstrip()
            #id_esperando = primeiroSemACK(janelaDeslizante)
            tamanho = len(mensagem)
            timestamp         = time.time() #para o seg e nanoseg serem da mesma base
            timestamp_sec     = int(timestamp)
            timestamp_nanosec = int((timestamp % 1)*(10 ** 9))
            
            if (fimJanela - inicioJanela == tamanho_janela):
                janelaLock.acquire()
                del janela[inicioJanela]
                inicioJanela  += 1
                janelaLock.release()

            janela[seqNum] = {'msg': mensagem, 'sec': timestamp_sec, 'nsec': timestamp_nanosec, 'acked': False}
            fimJanela += 1

            enviaPacote(seqNum)

            janela[seqNum]['timer'] = Timer(timeout, bateuTimer, [seqNum])
            janela[seqNum]['timer'].start()

            seqNum += 1

            if (fimJanela - inicioJanela == tamanho_janela):
                while(not janela[inicioJanela]['acked']):
                    print("janela travada no ", inicioJanela)
                    seqAck, correto = recebeACK()
                    if (correto):
                        janela[seqAck]['acked'] = True
                        janela[seqAck]['timer'].cancel()
                        print("cancelou timer")
                    else:
                        print("md5 errado ", seqAck)
                print("destravou")
                
    while (inicioJanela != fimJanela): 
        while(not janela[inicioJanela]['acked']):
            seqAck, correto = recebeACK()
            if (correto):
                janela[seqAck]['acked'] = True
                janela[seqAck]['timer'].cancel()
            else:
                print("2. md5 errado ", seqAck)
        
        inicioJanela  += 1

    udp.close()


##### EXECUCAO DO PROGRAMA #####    
janelaDeslizante()

