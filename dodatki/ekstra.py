#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import time
import datetime
import re
import os
from MultipartPostHandler import MultipartPostHandler
import threading
import sys
from test import *
from cookielib import  CookieJar, Cookie
import gzip
from StringIO import StringIO
import urllib, urllib2, httplib, socket
class BindableHTTPConnection(httplib.HTTPConnection):
    def connect(self):

        self.sock = socket.socket()
        self.sock.bind((self.source_ip, 0))
        if isinstance(self.timeout, float):
                self.sock.settimeout(self.timeout)
        self.sock.connect((self.host,self.port))

def BindableHTTPConnectionFactory(source_ip):
    def _get(host, port=None, strict=None, timeout=0):
        bhc=BindableHTTPConnection(host, port=port, strict=strict, timeout=timeout)
        bhc.source_ip=source_ip
        return bhc
    return _get

class BindableHTTPHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return self.do_open(BindableHTTPConnectionFactory(ip[0]), req)

def decgzip(data):
    buf = StringIO( data)
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    return data
def trader(img):
    APIKEY = "9f65e7f381c3af2b076ea680ae96b0b7"
    var = open(img,'rb')
    ab = var.read()
    var.close()
    var = ab.encode('base64')
    url = "http://api.captchatrader.com/submit"
    timestamp_form = {'api_key': APIKEY,
              'password': "killer5",
              'username': "soras5",
              'value': var}
    data = urllib.urlencode(timestamp_form)
    while 1:
        try:
            response = urllib2.urlopen(url,data).read()
            break
        except:
            print "CONN ERROR"
    response = eval(response)
    return response[1]

class signal(threading.Thread):
    def __init__(self):
        self.startuj = True
        threading.Thread.__init__(self)

    def run(self):
        self.startuj = True
        while self.startuj:
            sys.stdout.write("BEEP!\a\r")
            sys.stdout.flush()
            time.sleep(1)
            sys.stdout.write("                \r")
            sys.stdout.flush()
            time.sleep(1)

    def stop(self):
        self.startuj = False
        threading.Thread.__init__(self)

signal = signal()
class openurl(object):
    def __init__(self,multipart=False):
        self.headers= None
        self.opener = None
        self.cj = None
        self.ref = None
        self.multipart=multipart
        self.build_opener()

    def build_opener(self, proxy=None):
        self.headers = getheaders()
        self.cj = CookieJar()
        if self.multipart:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),
                                               urllib2.HTTPSHandler(debuglevel=0),MultipartPostHandler)
        else:
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),
                                               urllib2.HTTPSHandler(debuglevel=0))

    def rebuild(self):
        self.headers= None
        self.opener = None
        self.cj = None
        self.ref = None
        self.build_opener()

    def otworz(self, url, dane, ref=None,  addtoref=None,swoj=None):
        error = 0
        if not self.multipart:
            if dane:
                dane = urllib.urlencode(dane)
        req = urllib2.Request(url, dane, self.headers)
        if ref:
            if (ref == 'last' or ref == 'lastnot') and self.ref:
                req.add_header('Referer', self.ref)
            elif ref != 'not':
                req.add_header('Referer', ref)
        host = url.split("/")[2]
        req.add_header('Host', host)
        req.add_header('Connection', 'keep-alive')
        req.add_header('Accept-Encoding', 'gzip, deflate')
        req.add_header('Accept-Language', 'pl,en-us;q=0.7,en;q=0.3')

        if addtoref:
            for key, value in addtoref:
                req.add_header(key, value)
        while 1:
            try:
                response = self.opener.open(req)
                if ref != "not" and ref != "lastnot":
                    self.ref= url
                try:
                    if response.info()['content-encoding'] == 'gzip':
                        return decgzip(response.read())
                    else:
                        return response.read()
                except:
                    return response.read()
            except:
                internet()
                error += 1
                if error > 60:
                    if internet():
                        signal.start()
                        raw_input('ERROR NIE ZWIAZANY Z NIE DZIALAJACYM INTERNETEM (%s)\n'%(url))
                        signal.stop()
                sys.stdout.write("Timeout in openurl(%s) \r"%(error))
                sys.stdout.flush()
                time.sleep(error*0.5)

def getheaders():
    head = open('konkursy_base/dodatki/useragent.txt').readlines()
    # headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0" }
    headers = {"User-Agent":random.choice(head).strip()}
    # print headers
    return headers


def getrefer(name):
    """
    if typ:
        if typ == 'b':
            head = open('direct_babcia_ref').readlines()
            headers = random.choice(head).strip()
        elif typ == 'r':
            head = open('direct_ruda_ref').readlines()
            headers = random.choice(head).strip()
    else:
        head = open('mamy_ref_list').readlines()
        headers = random.choice(head).strip()
    """
    head = open("refy/"+name).readlines()
    headers = random.choice(head).strip()
    return headers

def get_time(unix):
    return (datetime.datetime.fromtimestamp(int(unix)).strftime('%Y-%m-%d %H:%M:%S'))
def spij(czas):
    time.sleep(czas)
def log(name, dane):
    to = get_time(time.time())+" "+dane
    print to
    a = open(name, 'a')
    a.write(to + "\n")
    a.close()
def spij_e():
    h = int(datetime.datetime.fromtimestamp(int(time.time())).strftime('%H'))

    if h > 1 and h < 3:
        czas = losuj(10,21)
    elif h > 2 and h < 6:
        czas = losuj(15,26)
    elif h > 5 and h < 8:
        czas = losuj(10,21)
    elif h > 7 and h < 11:
        czas = losuj(10,21)
    elif h > 10 and h < 14:
        czas = losuj(8,15)
    elif h > 13 and h < 18:
        czas = losuj(7,13)
    elif h > 17 and h < 20:
        czas = losuj(5,10)
    elif h == 20:
        czas = losuj(5,6)
    elif h > 20 and h < 23:
        czas = losuj(5,10)
    elif h > 22 or h == 0:
        czas = losuj(7,13)
    if h > 0 and h < 2:
        czas = losuj(8,15)

    c = 1334010505.6
    ru = time.time() - c
    ws = (((ru / (60*60*24)) / 10)*2) +1
    log("logs/mamy.txt", "Nastepne glosowanie za %s minut"%(int(czas*ws)))
    spij(czas*ws*60)


def get_action():
    """
        20% - direct
        20% - facebook
        60% - ref
    """
    los = losuj(1,101)
    if los < 21:
        return 3
    elif los < 41:
        return 1
    else:
        return 2

def saving(nazwa, data):
    a = open(nazwa, 'wb')
    a.write(data)
    a.close()
def scap(nazwa, data):
    a = open("html/%s"%(nazwa), 'wb')
    a.write(data)
    a.close()
def losuj(x,y):
    return random.randrange(x,y)
def pchar(s):
    return s.replace("ż","z").replace("ź","z").replace("ć","c").replace("ń","n").replace("ą","a").replace("ś","s").replace("ł","l").replace("ś","s").replace("ą","a").replace("ó","o").replace("ę","e").replace("Ł","L").replace("Ś","S").replace("Ń","N")
def send(data,shar=False):	
    data = urllib.urlencode({"a":repr(data)})
    url = "http://bivpn.pl/serwer/"
    if shar:
        url = "http://178.63.199.145/serwer/"
    error = 0
    while 1:
        try:
            response = urllib2.urlopen(url,data, timeout=180).read().replace("\n","").replace("\r","")
            break
        except:
            error += 1
            if error == 1:
                print "timeout"
            if error > 3:
                if internet():
                    signal.start()
                    raw_input('Serwer NIE ODPOWIADA NIE JEST TO NIE DZIALAJACYM INTERNETEM (%s)\n'%(data))
                    signal.stop()
            if error%100 == 0:
                print "timeout"
            time.sleep(0.2)

    return response
if __name__ == "__main__":
##    captcha_solve()
    ip=ip2()
    ip.stop()
