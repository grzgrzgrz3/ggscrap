#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, sys, string, telnetlib
import urllib2
from os import path
import random
import time
class ip(object):
    def __init__(self,nobuild=False):
        rand = str(random.randrange(1,99999))
        self.nobuild = nobuild
        self.dir = os.path.expanduser("~")+"\Pulpit\ipchange\\"
        self.zmiana_dir = self.dir+'zmiana'
        self.s_n = self.dir+str(rand)
        self.create()
    def start(self):
        print "BLOKADA IP ZWOLNIONA"
        if os.path.isfile(self.s_n+'stop'):
            os.rename(self.s_n+'stop',self.s_n+'start')
        elif os.path.isfile(self.s_n+'start'):
            pass
    def stop(self):
        if self.zmiana_check():
            print "W trakcie zmiany IP"
            while self.zmiana_check():
                time.sleep(0.2)
        print "SKRYPT BLOKUJE ZMIANE IP"
        if os.path.isfile(self.s_n+'stop'):
            pass
        elif os.path.isfile(self.s_n+'start'):
            os.rename(self.s_n+'start',self.s_n+'stop')
    def create(self):
        if not os.path.isfile(self.s_n+'stop') and not os.path.isfile(self.s_n+'start') and not os.path.isfile(self.s_n+'zmiana') and not self.nobuild:
            open(self.s_n+'start','w')
    def zmiana(self):
        if not self.zmiana_check():
            print 'Zmienia IP'
            open(self.zmiana_dir,'w')
    def zmiana_koniec(self):
        os.remove(self.zmiana_dir)
    def zmiana_check(self):
        if os.path.isfile(self.zmiana_dir):
            return True
        else:
            return False
    def pre_zmiana_check(self):
        lista = os.listdir(self.dir)
        for raw in lista:
            if raw.endswith('stop'):
                return False
        return True

ippp=ip(True)

def zmiana():
	count = 0
	if not ippp.pre_zmiana_check():
		print "Czeka na zakonczenie reszty skryptow"
		while not ippp.pre_zmiana_check():
			time.sleep(2)
	if not ippp.zmiana_check():
		ippp.zmiana()
		cmd = 'rasdial "nnetia" /DISCONNECT'
		os.system(cmd)
		while 1:
			try:
				urllib2.urlopen('http://google.pl',timeout=1)
				os.system(cmd)
				print "Nie rozlaczylo"
			except:
				break
		cmd = 'rasdial "nnetia" "1znjf77w@net24.com.pl" "JZmADfND"'
		os.system(cmd)
		count = 1
		while 1:
			if count%10 == 0:
				print "laczy ponownie"
				cmd = 'rasdial "nnetia" "1znjf77w@net24.com.pl" "JZmADfND"'
				os.system(cmd)
			try:
				urllib2.urlopen('http://google.pl',timeout=1)
				os.system(cmd)
				break
			except:
				count += 1
				time.sleep(0.5)
		ippp.zmiana_koniec()
		return True
	else:
		print 'Ip jest juz zmieniane'
		while ippp.zmiana_check():
			time.sleep(1)
	return True

if __name__ == "__main__":
	zmiana()
