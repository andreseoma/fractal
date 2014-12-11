from tkinter import *
from tkinter import ttk
from math import copysign, floor, fmod, ceil
from time import time
from numba import jit
import multiprocessing as mp
import queue
from PIL import Image, ImageTk
import numpy
import gmpy2
from gmpy2 import mpfr, mpc
import traceback
#kasutab lisaks mooduleid gmpy2, numpy, numba ja Pillow, mis tuleb tõmmata internetist


#@jit(nopython=True)    #arbitrary precision puhul välja kommenteerida
def image(img,minx,miny,d_x,n):
    py,px = img.shape
    stepx=d_x/px
    d_y = d_x * py/px
    stepy = d_y/py
    for y in range(py):
        for x in range(px):
            c=minx+x*stepx+1j*(miny+d_y-y*stepy)
            z=c
            col=n
            for i in range(n):
                z=z*z+c
                if z.real*z.real+z.imag*z.imag > 4:
                    col=i
                    break
            img[y,x]=255-255*col//n

def hit3(event):
    global start3
    start3=(event.x, event.y)

def drag3(event):
    global x, y, dpx
    dpx=max(abs(start3[0]-event.x)/sizex,abs(start3[1]-event.y)/sizey)
    x=start3[0]+copysign(dpx*sizex, event.x-start3[0])
    y=start3[1]+copysign(dpx*sizey, event.y-start3[1])
    canv.coords(rect,start3[0],start3[1],x,y)
    canv.itemconfig(rect,state='normal')

def drop3(event):
    global d_x, d_y, minx, miny
    canv.itemconfig(rect,state='hidden')
    if start3[0]==event.x or start3[1]==event.y:
        return
    x0,y0 = min(start3[0],x)+dx, sizey-max(start3[1],y)+dy
    minx, miny = minx+d_x*x0/sizex, miny+ d_y*y0/sizey
    d_x=d_x*dpx
    d_y=d_x*sizey/sizex
    reset()

def hit1(event):
    global start1, nodrag
    nodrag=False
    start1=(event.x, event.y)

def drag1(event):
    update(dx+start1[0]-event.x,dy+event.y-start1[1])

def drop1(event):
    global dx, dy, nodrag
    nodrag=True
    dx = dx+start1[0]-event.x
    dy = dy+event.y-start1[1]
    update(dx,dy)

def scroll(event):
    global d_x, d_y, minx, miny
    if event.delta<0:
        minx,miny=minx+dx/sizex*d_x-d_x/2,miny+dy/sizey*d_y-d_y/2
        d_x=2*d_x
        d_y=d_x*sizey/sizex
        reset()

def worker(jobs,done):
    while 1:
        job=jobs.get()
        try:
            if len(job) == 8:
                addjobs(job,jobs)
                continue
            tim=time()
            img=numpy.zeros((job[4],job[3]),dtype=numpy.uint8)
            image(img,job[0],job[1],job[2],job[6])
            done.put([img,job[5],time()-tim])
        except Exception as e:
            done.put([e,traceback.format_exc()])

def reset():
    global dx, dy, curi, curj, nodrag, readydata
    print('\'',minx,miny,d_x,'\'')
    readydata=set()
    nodrag=True
    curi,curj=0,0
    dx, dy = 0, 0
    grid=[(i,j) for i in range(rangei) for j in range(rangej)]
    grid+=[(i,j) for j in range(-extraj,rangej+extraj) for i in range(-extrai,0)]
    grid+=[(i,j) for j in range(-extraj,rangej+extraj) for i in range(rangei,rangei+extrai)]
    grid+=[(i,j) for i in range(0,rangei) for j in range(-extraj,0)]
    grid+=[(i,j) for i in range(0,rangei) for j in range(rangej,rangej+extraj)]
    work=map(jobforgrid,grid)
    while not jobs.empty():
        try: jobs.get_nowait()
        except: pass
    while not done.empty():
        try: done.get_nowait()
        except: pass
    for el in work: jobs.put(el)

def jobforgrid(coords):
    i,j=coords[0],coords[1]
    return [minx+i*d_x*gridx/sizex,miny+j*d_y*gridy/sizey,d_x*gridx/sizex,gridx,gridy,(i,j),n]

def addjobs(job,jobs):
    def jobforgrid2(coords):
        i,j=coords[0],coords[1]
        return [minx+i*d_x*gridx/sizex,miny+j*d_y*gridy/sizey,d_x*gridx/sizex,gridx,gridy,(i,j),n]
    curi,curj,minx, miny, d_x, d_y, readydata, g = job
    grid=[(i+curi,j+curj) for i in range(rangei) for j in range(rangej)]
    grid+=[(i+curi,j+curj) for j in range(-extraj,rangej+extraj) for i in range(-extrai,0)]
    grid+=[(i+curi,j+curj) for j in range(-extraj,rangej+extraj) for i in range(rangei,rangei+extrai)]
    grid+=[(i+curi,j+curj) for i in range(0,rangei) for j in range(-extraj,0)]
    grid+=[(i+curi,j+curj) for i in range(0,rangei) for j in range(rangej,rangej+extraj)]
    grid2=set()
    while 1:
        try:
            temp=jobs.get_nowait()
            grid2.add(temp[5])
        except queue.Empty: break
    for el in grid:
        if not(el in grid2 or el in readydata):
            jobs.put(jobforgrid2(el))

def update(dx,dy):
    global curi, curj
    i = floor(dx/gridx)
    j = floor(dy/gridy)
    if curi!=i or curj!=j:
        curi,curj=i,j
        jobs.put([curi,curj,minx, miny, d_x, d_y, readydata,0])
    offsetx=dx%gridx
    offsety=dy%gridy
    for m in range(rangei+2*extrai):
        for p in range(rangej+2*extraj):
            bigim.paste(griddata.get((i-extrai+m,j-extraj+p),zeroimg),(m*gridx,(rangej+2*extraj)*gridy-(1+p)*gridy))
    im.paste(bigim,(-gridx*extrai-offsetx,-gridy*extraj+offsety-(gridy-griddif)))
    img.paste(im)
    
def listener():
    gotsome=False
    while 1:
        try:
            job=done.get_nowait()
            gotsome=True
        except queue.Empty:
            if gotsome and nodrag:
                if (0 <= job[1][0]-curi <= rangei or 0 <= job[1][1]-curj <= rangej):
                    update(dx,dy)
            break
        else:
            if isinstance(job[0],Exception):
                raise Exception('\n'+''.join(job[1]))
            griddata[job[1]]=Image.fromarray(job[0],mode='L')
            readydata.add(job[1])
            #print(job[2]) #prindib pildi arvutamiseks kulunud aegu
    root.after(20,listener)

gmpy2.get_context().precision=100 #komakohtade arv arbitrary precision puhul
sizex=300
sizey=300
n=1300
gridx=250 #ühe arvutatava ruudu pikkus pikslites
gridy=250
rangei=ceil(sizex/gridx)
rangej=ceil(sizey/gridy)
extrai=ceil(rangei/2)
extraj=ceil(rangej/2)
griddif=sizey%gridy

if __name__=='__main__':
    #minx = mpfr('-2')
    #miny = mpfr('-2')
    #d_x=mpfr('4')
    minx = -2 #ilma arbitrary precisionita versioon, kõvasti kiirem
    miny = -1
    d_x = 4  #pildi pikkus mööda reaaltelge
    d_y = d_x *sizey/sizex  #pildi pikkus mööda komplekstelge
    griddata={}
    readydata=set()
    jobs=mp.Queue()
    done=mp.Queue()
    zeroimg=Image.new('L',(gridx,gridy))
    reset()
    procs = [mp.Process(target=worker,args=(jobs,done),daemon=True) for i in range(4)]
    for proc in procs: proc.start()
    root = Tk()
    canv = Canvas(root,width=sizex,height=sizey)
    canv.pack()
    bigim=Image.new('L',((rangei+2*ceil(rangei/2))*gridx,(rangej+2*ceil(rangej/2))*gridy))
    im=Image.new('L',(sizex,sizey))
    img=ImageTk.PhotoImage('L',(sizex,sizey))
    imag=canv.create_image(0,0,image=img,anchor='nw')
    rect=canv.create_rectangle(50,50,200,200,state='hidden')
    canv.bind('<Button-3>', hit3)
    canv.bind('<B3-Motion>', drag3)
    canv.bind('<ButtonRelease-3>',drop3)
    canv.bind('<Button-1>', hit1)
    canv.bind('<B1-Motion>', drag1)
    canv.bind('<ButtonRelease-1>',drop1)
    canv.bind('<MouseWheel>', scroll)
    root.after(0,listener)
    root.mainloop()
    for proc in procs: proc.terminate()
