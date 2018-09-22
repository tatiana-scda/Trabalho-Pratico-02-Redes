import hashlib
import time
import bitstring
import sys
import thread

tamanho_janela = 4
janelaDeslizante = {}
arquivo = sys.argv[1]
timeout = sys.argv[2]
janelaDeslizanteTempos = {}
janelaDeslizantePacotes = {}
desvioJanela = 0

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
    pacote                      = bytearray([])
    pacote[0:8]                 = bitstring.BitArray(uint=num_seq, length=64).bytes
    pacote[8:16]                = bitstring.BitArray(uint=timestamp_seg, length=64).bytes
    pacote[16:20] = bitstring.BitArray(uint=timestamp_nanoseg, length=32).bytes
    pacote[20:22] = bitstring.BitArray(uint=len(mensagem), length=16).bytes
    pacote.extend(map(ord, mensagem))
    pacote                      = calculaMD5(pacote, 22+len(mensagem))
    print(pacote)
    return pacote

def processarArquivo():
    with open(arquivo) as file:
        temp = 0
        while True:
            while temp < tamanho_janela-1: #-1 pois tem de ter um espaco de buffer
                id_pacote = temp + desvioJanela
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
                janelaDeslizanteTempos[id_pacote] = time.time()
                janelaDeslizantePacotes[id_pacote] = pacote
            
            posicao = 0
            for i in range(0, tamanho_janela-1):
                if janelaDeslizanteTempos[i] == float("inf"):
                    posicao = posicao + 1

def checarTimeout():
    while True:
        for i in range(0, tamanho_janela-1):
            tempo = time.time() - janelaDeslizanteTempos[i]
            if tempo > timeout:
                tcp.send(janelaDeslizantePacotes[i])
                janelaDeslizanteTempos[i] = time.time()
        time.sleep(timeout)

def recebendoPacoteACK():
        #pacote            = tcp.recv(36)
        if(calculaMD5ACK(pacote)): #se o md5 funcionar para o pacote
            seqNum = pacote[0:8]
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            janelaDeslizante[seqNum] = True #checaJanela(janelaDeslizante)
            janelaDeslizanteTempos[seqNum] = float("inf") #esvaziando janela
        else: print(pacote)

processarArquivo()
