#!/usr/bin/env python3

import hashlib
import time
import bitstring
import sys
import threading

tamanho_janela = 4
arquivo_entrada = sys.argv[1]
timeout = sys.argv[2]
janelaDeslizanteTempos = {}
janelaDeslizantePacotes = {}
janelaDeslizanteRecebidos = {}
primeiro_janela = 0

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
    if len(janelaDeslizanteTempos) == tamanho_janela:
        esta_enviado = True
        for chave, valor in janelaDeslizantesRecebidos:
            if valor == False: 
                esta_enviado = False
        if esta_enviado:
            janelaDeslizanteTempos    = {}
            janelaDeslizantePacotes   = {}
            janelaDeslizanteRecebidos = {}
        return True
    return False

def processarArquivo():
    with open(arquivo_entrada) as file:
        id_pacote = 0
        tempo_passado = time.clock() - timeout
        while True: 
            for i in range(primeiro_janela, primeiro_janela + tamanho_janela):
                if janelaDeslizanteTempos[i] != None:
                    tempo = time.clock() - janelaDeslizanteTempos[i]
                    if tempo > timeout:
                        tcp.send(janelaDeslizantePacotes[i]
                        janelaDeslizanteTempos[i] = time.clock()


            while !janelaEstaCheia(): #-1 pois tem de ter um espaco de buffer
                mensagem          = file.readline()
                
                #timestamp         = time.time_ns()
                #timestamp_sec     = int(timestamp / (10 ** 9))
                #timestamp_nanosec = timestamp % (10 ** 9)
                timestamp_sec = 1324894851
                timestamp_nanosec = 5258448
                
                pacote            = criadorPacote(id_pacote, timestamp_sec, timestamp_nanosec, mensagem)
                #print(pacote)
                id_pacote = id_pacote + 1
                #tcp.send(pacote) - enviaPacote
                janelaDeslizantePacotes[id_pacote] = pacote
                janelaDeslizanteTempos[id_pacote]  = time.time()
                id_pacote = id_pacote+1

def recebendoPacoteACK():
        pacote = tcp.recv(36)
        if(calculaMD5ACK(pacote)): #se o md5 funcionar para o pacote
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            janelaDeslizanteRecebidos[seqNum] = True
 
threading.Thread(target = recebendoPacoteACK, args = (tcp, arquivo_saida, )).start()
threading.Thread(target = processarArquivo,   args = (tcp, arquivo_entrada, )).start()
