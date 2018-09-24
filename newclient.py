#!/usr/bin/env python3

import random
import socket
import hashlib
import time
import bitstring
import sys
#import threading
from threading import Timer
from collections import defaultdict

arquivo_entrada             = sys.argv[1]
ip_port                     = sys.argv[2]
tamanho_janela              = int(sys.argv[3])
timeout                     = int(sys.argv[4])
md5_erro                    = float(sys.argv[5])
#threads                    = {} 
janelaDeslizante            = {}  
linhas                      = []
janelaCheia                 = 0

HOST = ip_port[0:ip_port.find(':')]
PORT = int(ip_port[ip_port.find(':')+1:])
udp  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(timeout)
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
    if random.random() < md5_erro:
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
    return pacote

def recebendoPacote(janelaDeslizante, arquivo_entrada, udp, dest, timeout):
    global janelaDeslizante

    pacote = udp.recvfrom(36)[0]
    for pack in len(arquivo_entrada)
        if(calculaMD5ACK(pacote)): #se o md5 funcionar para o pacote
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #bytearray para int
            janelaDeslizante[seqnum].timer = Timer(timeout, handler, [self]) #confere time out e envia ou cancela ack
            janelaCheia +=1


def preencherDicts(arquivo_entrada):
    global threads, janelaDeslizante, linhas
    with open(arquivo_entrada, "r") as file:
        arquivo = file.readlines()
    linhas = arquivo


def primeiroSemACK(janelaDeslizanteACKRecebido):
    for posicao in range(len(janelaDeslizanteACKRecebido)):
        if janelaDeslizanteACKRecebido[posicao] == False:
            return posicao #posicao do pacote que ainda nao foi recebida a confirmacao ACK
        else:
            return -1


def enviarPacote(udp, dest, timeout):
    global janelaCheia

    while (janelaCheia < tamanho_janela):
        timestamp         = time.time() #para o seg e nanoseg serem da mesma base
        timestamp_sec     = int(timestamp)
        timestamp_nanosec = int((timestamp % 1)*(10 ** 9))

        #criacao do pacote
        pacote            = criadorPacote(id_pacote, timestamp_sec, timestamp_nanosec, mensagem)
        udp.sendto(pacote, dest) #envia_pacote

        for i in range len(arquivo_entrada):
            while janelaDeslizante[i] != True:
                recebendoPacote(janelaDeslizante, arquivo_entrada, udp, dest, timeout) #incrementa janela
    except Exception as e:
        if janelaDeslizante[i]:
        enviarPacote(udp, dest, timeout)


 def janelaDeslizante(tamanho_janela, udp, dest, timeout):
    global tamanho_janela, udp, dest, timeout
    while(not janelaCheia):
        preencherDicts(arquivo_entrada) #de acordo com a entrada, preenche os dicts
        id_esperando = primeiroSemACK(janelaDeslizante)

        for i in len(arquivo_entrada):
            enviarPacote(udp, dest, timeout)
            recebendoPacote(janelaDeslizante, arquivo_entrada, udp, dest, timeout)
        udp.close()


##### EXECUCAO DO PROGRAMA #####    
janelaDeslizante()

