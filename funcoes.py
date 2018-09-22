import hashlib
import time
import bitstring

def calculaMD5(quadro, comeco):
    m                        = hashlib.md5()
    md5                      = m.update(quadro)
    md5                      = m.digest()
    quadro[comeco:comeco+16] = md5
    return quadro

def criadorQuadro(num_seq, timestamp_seg, timestamp_nanoseg, mensagem):
    quadro                      = bytearray([])
    quadro[0:8]                 = bitstring.BitArray(uint=num_seq, length=64).bytes
    quadro[8:16]                = bitstring.BitArray(uint=timestamp_seg, length=64).bytes
    quadro[16:20]               = bitstring.BitArray(uint=timestamp_nanoseg, length=32).bytes
    quadro[20:22]               = bitstring.BitArray(uint=len(mensagem), length=16).bytes
    quadro.extend(map(ord, mensagem))
    quadro                      = calculaMD5(quadro, 22+len(mensagem))
    print(quadro)
    return quadro

mensagem = 'ola mundo'
seg = 1537571605
nano = 394989
import numpy as np
criadorQuadro(1, seg, nano, mensagem)

