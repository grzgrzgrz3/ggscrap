import time
from pymouse import PyMouse
import os
import numpy
import random
from PIL import ImageGrab
from PIL import Image
import win32com.client as comclt
wsh= comclt.Dispatch("WScript.Shell")

def getpixel():
    m = PyMouse()
    poz = m.position()
    return ImageGrab.grab(bbox=(poz[0]-1,poz[1]-1,poz[0],poz[1])).load()[0,0]

def poz():
    m = PyMouse()
    return m.position()

def saveimage(box):
    ImageGrab.grab(bbox=box).save('nowe/%s.png'%(random.randrange(1,1000)),'BMP')


def ciecie(ar):
    
    box1a=(4,4,18,29)
    box1b=(4,36,18,64)
    box2a=(20,4,40,29)
    box2b=(20,36,40,64)
    ar = Image.open(os.getcwd()+'/nowe/76.png')
    ar.crop(box1a).save('nowe/1a%s.bmp'%(random.randrange(1,1000)))
    ar.crop(box1b).save('nowe/1b%s.bmp'%(random.randrange(1,1000)))
    ar.crop(box2a).save('nowe/2a%s.bmp'%(random.randrange(1,1000)))
    ar.crop(box2b).save('nowe/2b%s.bmp'%(random.randrange(1,1000)))
def gethand():
    box1a=(4,4,18,29)
    box1b=(4,36,18,64)
    box2a=(20,4,40,29)
    box2b=(20,36,40,64)
    im = ImageGrab.grab(bbox=(471,419,535,489))
    #ciecie(im)
    wn = []
    lfig =im.crop(box1a)
    lcol = im.crop(box1b)
    wyn = left(lfig,lcol)
    figura, color = wyn
    figura = sorted(figura)
    color = sorted(color)
    wn.append(figura[0][1][0]+color[0][1][0])
    
    pfig =im.crop(box2a)
    pcol = im.crop(box2b)
    wyn = right(pfig,pcol)
    figura, color = wyn
    figura = sorted(figura)
    color = sorted(color)
    wn.append(figura[0][1][0]+color[0][1][0])

    return wn
def left(n,n1):
    odpf = []
    odpc = []
    for nazwa in os.listdir(os.getcwd()+'/karty/lfig'):
        ist = Image.open(os.getcwd()+'/karty/lfig/'+nazwa)
        wyn = comp(ist,n)
        #print nazwa, n, wyn
        odpf.append([wyn,nazwa])
    for nazwa in os.listdir(os.getcwd()+'/karty/lcol'):
        ist = Image.open(os.getcwd()+'/karty/lcol/'+nazwa)
        wyn = comp(ist,n1)
        #print nazwa, n, wyn
        odpc.append([wyn,nazwa])
    return [odpf,odpc]

def right(n,n1):
    odpf = []
    odpc = []
    for nazwa in os.listdir(os.getcwd()+'/karty/pfig'):
        ist = Image.open(os.getcwd()+'/karty/pfig/'+nazwa)
        wyn = comp(ist,n)
        #print nazwa, n, wyn
        odpf.append([wyn,nazwa])
    for nazwa in os.listdir(os.getcwd()+'/karty/pcol'):
        ist = Image.open(os.getcwd()+'/karty/pcol/'+nazwa)
        wyn = comp(ist,n1)
        #print nazwa, n, wyn
        odpc.append([wyn,nazwa])
    return [odpf,odpc]
def getcards():
    im = ImageGrab.grab(bbox=(380,262,622,331))
    imp = im.load()
    start = False
    full = []
    for x in range(0,im.size[0]):
        if not start:
            if imp[x,30] == (220,220,220):
                start = x
        else:
            if imp[x,30] == (219,219,219):
                full.append((start,3,x,69))
                start = False

    wn = []
    for a in full:
        ar = im.crop(a)
        wyn = compare(ar)
        figura, color = wyn
        figura = sorted(figura)
        color = sorted(color)
        wn.append(figura[0][1][0]+color[0][1][0])
    return wn    

def compare(n):
    odpc = []
    odpf = []
    #ar = Image.open(os.getcwd()+'/nowe/'+n)
    ar = n
    ar1 = ar.crop(box=(2,2,23,30))
    ar2 = ar.crop(box=(1,30,25,55))
    for nazwa in os.listdir(os.getcwd()+'/karty/fig'):
        ist = Image.open(os.getcwd()+'/karty/fig/'+nazwa)
        wyn = comp(ist,ar1)
        #print nazwa, n, wyn
        odpf.append([wyn,nazwa])
    for nazwa in os.listdir(os.getcwd()+'/karty/col'):
        ist = Image.open(os.getcwd()+'/karty/col/'+nazwa)
        wyn = comp(ist,ar2)
        #print nazwa, n, wyn
        odpc.append([wyn,nazwa])
    return [odpf,odpc]

def dealer():
    lista = [['P8', [['P8a.png', (742L, 212L, 762L, 232L)], ['P8b.png', (742L, 202L, 762L, 222L)]]],['P9', [['P9a.png', (741L, 349L, 761L, 369L)], ['P9b.png', (741L, 340L, 761L, 360L)]]],['P10',[['P10a.png', (581L, 379L, 601L, 399L)],['P10b.png', (579L, 368L, 599L, 388L)]]],['P2', [['P2a.png', (257L, 381L, 277L, 401L)], ['P2b.png', (259L, 364L, 279L, 384L)]]],['P3', [['P3a.png', (98L, 347L, 118L, 367L)], ['P3b.png', (98L, 341L, 118L, 361L)]]],['P4', [['P4a.png',(99L, 208L, 119L, 228L)], ['P4b.png', (97L, 201L, 117L, 221L)]]],['P5', [['P5a.png', (259L, 145L, 279L, 165L)]]],['P6', [['P6a.png', (420L, 146L, 440L, 166L)]]],['P7', [['P7a.png', (580L, 145L, 600L, 165L)]]],['P1',[['P1a.png', (419L, 377L, 439L, 397L)], ['P1b.png', (422L, 365L, 442L, 385L)]]]]
    for dil in lista:
        numer = dil[0]
        for x in dil[1]:
            box = x[1]
            name = x[0]
            img1 = Image.open(os.getcwd()+'/dealer/'+name)
            img2 = ImageGrab.grab(bbox=box)
            if  comp(img1,img2) < 300:
                return numer
    ImageGrab.grab().save(os.getcwd()+'/er/%s.png'%(random.randrange(1,1000)),'BMP')
    return "error"
def nh():
    ndeal = dealer()
    while 1:
        ndeal = dealer()
        if ndeal != dealerb and ndeal != 'error':
            return True
def folow_dealer():
    dealerb = None
    while 1:
        ndeal = dealer()
        if ndeal != dealerb and ndeal != 'error':
            print "Nowe rozdanie, nowy dealer:", ndeal
            dealerb = ndeal
            in_list()
        time.sleep(0.5)

def in_list():
    listaa = []
    lista = [['P2', [['P2a.png', (383L, 408L, 386L, 416L)], ['P2b.png', (386L, 409L, 389L, 417L)]]], ['P3', [['P3a.png', (224L, 377L, 227L, 385L)], ['P3b.png', (221L, 384L, 224L, 392L)]]], ['P4', [['P4a.png', (129L, 239L, 132L, 247L)], ['P4b.png', (128L, 245L, 131L, 253L)]]], ['P5', [['P5a.png', (291L, 174L, 294L, 182L)], ['P5b.png', (291L, 186L, 294L, 194L)]]], ['P6', [['P6a.png', (452L, 175L, 455L, 183L)], ['P6b.png', (452L, 185L, 455L, 193L)]]], ['P7', [['P7a.png', (612L, 174L, 615L, 182L)], ['P7b.png', (614L, 185L, 617L, 193L)]]], ['P8', [['P8a.png', (865L, 239L, 868L, 247L)], ['P8b.png', (854L, 244L, 857L, 252L)]]], ['P1', [['P1a.png', (543L, 407L, 546L, 415L)], ['P1b.png', (543L, 409L, 546L, 417L)]]], ['P9', [['P9a.png', (867L, 376L, 870L,384L)], ['P9b.png', (867L, 382L, 870L, 390L)]]], ['P10', [['P10a.png', (707L, 407L, 710L, 415L)], ['P10b.png', (699L, 408L,702L, 416L)]]]]
    #lista = [['P1', [['P1a.png', (436L, 399L, 448L, 403L)], ['P1b.png', (436L, 399L, 448L, 403L)]]], ['P2', [['P2a.png', (274L, 398L, 286L, 402L)], ['P2b.png', (274L, 398L, 286L, 402L)]]], ['P3', [['P3a.png', (115L, 367L, 127L, 371L)], ['P3b.png', (115L, 367L, 127L, 371L)]]], ['P5', [['P5b.png', (275L, 172L, 287L, 176L)], ['P5a.png', (275L, 172L, 287L, 176L)]]], ['P7', [['P7b.png', (597L, 172L, 609L, 176L)], ['P7a.png', (597L, 172L, 609L, 176L)]]], ['P8', [['P8a.png', (757L, 232L, 769L, 236L)], ['P8b.png', (757L, 232L, 769L, 236L)]]], ['P10', [['P10a.png', (714L, 403L, 726L, 407L)], ['P10b.png', (714L, 403L, 726L, 407L)]]], ['P4', [['P4a.png', (232L, 234L, 244L, 238L)], ['P4b.png', (232L, 234L, 244L, 238L)]]], ['P6', [['P6a.png', (554L, 172L, 566L, 176L)], ['P6b.png', (554L, 172L, 566L, 176L)]]], ['P9', [['P9a.png', (757L, 370L, 769L,374L)], ['P9b.png', (757L, 370L, 769L, 374L)]]]]
    for place in lista:
        numer = place[0]
        for x in place[1]:
            box = x[1]
            name = x[0]    
            img1 = Image.open(os.getcwd()+'/actions/'+name)
            img2 = ImageGrab.grab(bbox=box)
            if comp(img1,img2)== 0:
                listaa.append(numer)
                break
    return listaa

def find_cur(numern=None):
    lista = [['P1', [['P1a.png', (447L, 383L, 477L, 393L)]]], ['P2', [['P2a.png', (285L, 384L, 315L, 394L)]]], ['P3', [['P3a.png', (124L, 360L, 154L, 370L)]]], ['P6', [['P6a.png', (446L, 162L, 476L, 172L)]]], ['P7', [['P7a.png', (603L, 162L, 633L, 172L)]]],['P4', [['P4a.png', (127L, 220L, 157L, 230L)]]], ['P8', [['P8a.png', (767L, 221L,797L, 231L)]]], ['P9', [['P9a.png', (767L, 359L, 797L, 369L)]]], ['P5', [['P5a.png', (287L, 162L, 317L, 172L)]]], ['P10', [['P10a.png', (608L, 384L, 638L, 394L)]]]]
    if numern:
        for place in lista:
            numer = place[0]
            if numer == numern:
                for x in place[1]:
                    box = x[1]
                    name = x[0]    
                    img1 = Image.open(os.getcwd()+'/move/'+name)
                    img2 = ImageGrab.grab(bbox=box)
                    if comp(img1,img2)== 0:
                        return True
        return False
    for place in lista:
        numer = place[0]
        for x in place[1]:
            box = x[1]
            name = x[0]    
            img1 = Image.open(os.getcwd()+'/move/'+name)
            img2 = ImageGrab.grab(bbox=box)
            if comp(img1,img2)== 0:
                return numer
def all_in(a=None):
    m = PyMouse()
    if a:
        time.sleep(a)
    k = (679,558)
    m.click(k[0],k[1], 1)
    for a in range(0,13):
        wsh.SendKeys("9")
    wsh.SendKeys("{ENTER} ")
    wsh.SendKeys("{F3}")

def pasuj(a=None):
    if a:
        time.sleep(a)
    wsh.SendKeys("{F1}")

def action_track():
    while 1:
        act = find_cur()
        print "Teraz kolej: ",act
        cz = find_cur(act)
        while cz:
            cz = find_cur(act)
def reg(nu,name,call):
    m = PyMouse()
    poz = m.position()
    #dealer##box = (poz[0] -15,poz[1]-5,poz[0]+15,poz[1]+5)
    box = (poz[0] -35,poz[1]-15,poz[0]+35,poz[1]+15)   
    got = False
    for t in call:
        if t[0] == nu:
            t[1].append([nu+name+'.png',box])
            got = True
            break
    if not got:
        call.append([nu,[[nu+name+'.png',box]]])
    ImageGrab.grab(bbox=box).save('add/%s'%(nu+name+'.png'),'BMP')
def rebuy():
    m = PyMouse()
    m.press(496,403,1)
    wsh.SendKeys("{ENTER} ")
def rebuycheck():
    ll = [['rebuy.png',(410, 225, 480,255)]]
    for l in ll:
        box = l[1]
        name = l[0]    
        img1 = Image.open(os.getcwd()+'/add/'+name)
        img2 = ImageGrab.grab(bbox=box)
        if comp(img1,img2)== 0:
            return True
    return False
def comp(n1,n2):
    img1 = n1
    img2 = n2

    if img1.size != img2.size or img1.getbands() != img2.getbands():
        return -1

    s = 0
    for band_index, band in enumerate(img1.getbands()):
        m1 = numpy.array([p[band_index] for p in img1.getdata()]).reshape(*img1.size)
        m2 = numpy.array([p[band_index] for p in img2.getdata()]).reshape(*img2.size)
        s += numpy.sum(numpy.abs(m1-m2))
    return s
"40 21/A1 664692983"
"""
wsh.SendKeys("a") # send the keys you want
"""
