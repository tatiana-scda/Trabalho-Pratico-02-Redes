import hashlib
import time
import bitstring

janelaDeslizante = {}

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
    pacote[0:8]                 = bitstring.BitArray(uint=num_seq, length=64).bytes
    pacote[8:16]                = bitstring.BitArray(uint=timestamp_seg, length=64).bytes
    pacote[16:20]               = bitstring.BitArray(uint=timestamp_nanoseg, length=32).bytes
    pacote                      = calculaMD5ACK(pacote)
    print(pacote)
    return pacote

def recebendoPacote(pacote):#ACK
        #pacote            = tcp.recv(36)
        if(calculaMD5Pacote(pacote)): #se o md5 funcionar para o pacote
            seqNum = pacote[0:8]
            import pdb;pdb.set_trace()
            seqNum = int.from_bytes(seqNum, byteorder='big', signed=False) #transformar de bytearray para int
            janelaDeslizante[seqNum] = True #checaJanela(janelaDeslizante)
        else: print(pacote)

mensagem = 'ola mundo'
seg = 1537571605
nano = 394989
pacote = criadorPacoteACK(1, seg, nano)
#recebendoPacote(pacote)

