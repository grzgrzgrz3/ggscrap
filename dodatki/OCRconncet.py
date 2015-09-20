#!/usr/bin/env python
#-*- coding: utf-8 -*-
import time
import socket
import struct
ocrhost = '63.223.120.252'
ocrport = 4081
def resolv(n):
##    data = open('../html/%s'%n,'rb').read()
    data = n
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
            print "[ERROR] %s\n" % msg[1]
            return False
    try:
        sock.connect((ocrhost, ocrport))
    except socket.error, msg:
        print "[ERROR] %s\n" % msg[1]
        return False
    sock.send("\x00")
    sock.send(struct.pack('L',len(data)))
    sock.send(data)
    ans = sock.recv(1024).replace('\x00','')
    print [ans]
    if ord(ans) == 1:
        pass
    elif ord(ans) == 0:
        return False
    ans = False
    while not ans:
        ans = sock.recv(1024).replace('\x00','')
    sock.close()
    return ans[1:]


if __name__ == "__main__":

    path_to_image = 'captcha.png'
    answer = resolv(path_to_image)
    if answer:
        print "OCR response: ",answer