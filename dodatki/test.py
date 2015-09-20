try:
    import win32gui, win32con
    import win32api
    from pymouse import PyMouse
except ImportError:
    pass
import time
import urllib2
import random
import os
import threading
# from windows import PyMouse

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
def losuj(x,y):
	return random.randrange(x,y)
signal = signal
toplist = []
winlist = []
class ip(object):
    def __init__(self,nobuild=False):
        rand = str(losuj(1,99999))
        self.nobuild = nobuild
        self.dir = os.path.expanduser("~")+"\Pulpit\ipchange\\"
        if os.name == 'posix':
            self.dir = '/tmp/'
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
def ipchange():
	count = 0
	if not ippp.pre_zmiana_check():
		print "Czeka na zakonczenie reszty skryptow"
		while not ippp.pre_zmiana_check():
			time.sleep(2)
	if not ippp.zmiana_check():
		ippp.zmiana()
		name, typ = getwindowname()
		if name:
			focus(name)
			klik(name, typ)
			time.sleep(2)
			error = 0
			totalerror = 0
			while 1:
				if connection_check():
					break
				else:
					time.sleep(2*(totalerror+1))
					error += 1
				if error > 5:
					klik(name, 'extra')
					totalerror += 1
					error = 0
				if totalerror > 10:
					return False
			ippp.zmiana_koniec()
			return True
	else:
		print 'Ip jest juz zmieniane'
		while ippp.zmiana_check():
			time.sleep(1)
	return True


def randomclick():
    x = losuj(1,500)
    y = losuj(1,500)
    m = PyMouse()
    m.press(x,y,1)
def klik(name, typ):
    rect = win32gui.GetWindowRect(name)
    m = PyMouse()
    if typ == 'pc':
        x = rect[0]+92
        y = rect[1]+406
        win32api.SetCursorPos((x,y))
        time.sleep(0.5)
        m.press(x,y,1)
        time.sleep(4)
        m.press(x,y,1)
    elif typ == "play":
        x = rect[0]+620
        y = rect[1]+207 
        win32api.SetCursorPos((x,y))
        time.sleep(0.5)
        m.press(x,y,1)
        time.sleep(4)
        m.press(x,y,1)
    elif typ == "extra":
		x = rect[0]+620
		y = rect[1]+207 
		win32api.SetCursorPos((x,y))
		time.sleep(0.5)
		m.press(x,y,1)
		x = x - 255
		y = y + 102
		m.press(x,y,1)
def getwindowname():
	win32gui.EnumWindows(enum_callback, toplist)
	pcsuite = [(hwnd, title) for hwnd, title in winlist if 'one' in title.lower()]
	if pcsuite:
		return pcsuite[0][0], 'pc'
	play = [(hwnd, title) for hwnd, title in winlist if 'play' in title.lower()]
	if play:
		return play[0][0], 'play'
	return False, False
def enum_callback(hwnd, result):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

def focus(name):
    #win32gui.EnumWindows(enum_callback, toplist)
    #firefox = [(hwnd, title) for hwnd, title in winlist if 'one' in title.lower()]
    #print firefox
    #firefox = firefox[0]
    #win32gui.SetActiveWindow(firefox[0])
    #win32gui.SetFocus(firefox[0])
    #win32gui.SetForegroundWindow(name)
    while 1:
        try:
            win32gui.ShowWindow(name, win32con.SW_RESTORE)
            break
        except:
            print " Foucs error1"
    while 1:
        try:
            win32gui.SetForegroundWindow(name)
            break
        except:
            randomclick()
            time.sleep(3)
            print "Focus error2"

def naprawiac():
	a = open('dodatki/nap.txt').read()
	if a == 'tak':
		return False
	else:
		return True
def update_naprawia(a):
	print "NAPRAWIA: ", a
	b = open('dodatki/nap.txt','w')
	b.write(a)
	b.close()
	
def internet():
	if connection_check():
		return True
	else:
		print "Nie ma internetu"
		if naprawiac():
			update_naprawia('tak')
			name, typ = getwindowname()
			start = time.time()+300
			while start > time.time():
				klik(name, 'extra')
				time.sleep(10)
				if connection_check():
					update_naprawia('nie')
					return False
			print "Nie ma internetu"
			signal.start()
			while not connection_check():
				time.sleep(10)
			signal.stop()
			update_naprawia('nie')
			return False
		else:
			while not naprawiac():
				time.sleep(1)
def connection_check():
	for a in range(4):
		try:
			response=urllib2.urlopen('http://google.pl',timeout=5)
			return True
		except urllib2.URLError as err:
			time.sleep(1)
	return False	

if __name__ == "__main__":
    """
    connection = connection_check()
    print connection
    hwnd = focus()
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]+92
    y = rect[1]+406
    win32api.SetCursorPos((x,y))
    m = PyMouse()
    m.press(x,y,1)
    time.sleep(2)
    m.press(x,y,1)
        #ipchange()
    #print win32gui.GetCursorInfo()[2]
    name = getwindowname()[0]
    focus(name)
    rect = win32gui.GetWindowRect(name)
    #sizeh = rect[2]
    #sizew = rect[3]
    #roznicah = 780 - sizeh
    #roznicaw = 572 - sizew
    #przesuniecieh = rect[0] + roznicah
    #przesunieciew = rect[1] + roznicaw
    print rect
    #win32gui.SetWindowPos(name, win32con.HWND_TOP, przesuniecieh, przesunieciew, 780, 572,win32con.SW_RESTORE)
    x = rect[0]+620
    y = rect[1]+207
    win32api.SetCursorPos((x,y))
    """
    ipchange()