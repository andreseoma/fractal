from tkinter import *
from tkinter import ttk
from math import copysign, floor, fmod
from time import time
from numba import jit
import multiprocessing as mp
from PIL import Image, ImageTk
import numpy
#kasutab lisaks mooduleid numpy, numba ja Pillow, mis tuleb tõmmata internetist

@jit
def iterate(x,y,n):
    z=0.0j
    c=complex(x,y)
    for i in range(n):
        z=z*z+c
        if (z*z.conjugate()).real > 4: return i
    return n

@jit            
def image(minx,miny,d,px):
    step=d/px
    img=numpy.zeros((px,px),dtype=numpy.uint8)
    for y in range(px):
        for x in range(px):
            col=iterate(minx+x*step,miny+d-y*step,1000)
            img[y,x]=255-col
    return img

def hit3(event):
    global start3
    start3=(event.x, event.y)

def drag3(event):
    global start3, x, y, dpx
    dpx=max(abs(start3[0]-event.x),abs(start3[1]-event.y))
    x=start3[0]+copysign(dpx, event.x-start3[0])
    y=start3[1]+copysign(dpx, event.y-start3[1])
    canv.coords(rect,start3[0],start3[1],x,y)
    canv.itemconfig(rect,state='normal')

def drop3(event):
    global start3, x, y, d, dpx, minx, miny, dx, dy
    canv.itemconfig(rect,state='hidden')
    if start3[0]==event.x or start3[1]==event.y:
        return
    x0,y0 = min(start3[0],x)+dx, size-max(start3[1],y)+dy
    minx, miny = minx+d*x0/size, miny+ d*y0/size
    d=d*dpx/size
    print(minx,miny,d)
    reset()

def hit1(event):
    global start1, dx, dy, nodrag
    nodrag=False
    #print(dx, dy)
    start1=(event.x, event.y)

def drag1(event):
    global dx, dy
    update(dx+start1[0]-event.x,dy+event.y-start1[1])

def drop1(event):
    global dx, dy, nodrag
    nodrag=True
    dx = dx+start1[0]-event.x
    dy = dy+event.y-start1[1]
    #print(dx,dy)

def scroll(event):
    global d,minx,miny
    if event.delta<0:
        minx,miny=minx+dx/size*d-d/2,miny+dy/size*d-d/2
        d=2*d
        reset()

def worker(jobs,done):
    while 1:
        job=jobs.get()
        tim=time()
        img=image(job[0],job[1],job[2],job[3])
        done.put([img,job[0],job[1],job[4],time()-tim])

def reset():
    global grid, dx, dy, curi, curj,nodrag
    nodrag=True
    curi,curj=0,0
    dx, dy = 0, 0
    grid=[(i,j) for i in range(2) for j in range(2)]
    grid+=[(i,j) for j in range(-1,3) for i in (-1,2)]
    grid+=[(i,j) for i in (0,1) for j in (-1,2)]
    #print(grid)
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
    return [minx+i*d/2,miny+j*d/2,d/2,size/2,(i,j)]

def addjobs():
    global grid, curi, curj
    for i in range(-1,3):
        for j in range(-1,3):
            if (curi+i,curj+j) not in grid:
                grid+=[(curi+i,curj+j)]
                #print((curi+i,curj+j))
                #print(grid)
                jobs.put(jobforgrid((curi+i,curj+j)))

def update(dx,dy):
    global curi, curj
    i = floor(dx/(size/2))
    j = floor(dy/(size/2))
    if curi!=i or curj!=j:
        curi,curj=i,j
        addjobs()
    offsetx=dx%(size//2)
    offsety=dy%(size//2)
    #print(i,j,dx,dy,offsetx,offsety)
    for m in range(4):
        for n in range(4):
            #try:
            bigim.paste(griddata.get((i-1+m,j-1+n),zeroimg),(m*size//2,2*size-(1+n)*size//2))
            #except: pass
    #bigim.show()
    #im.paste(bigim,(size//2+offsetx,size-offsety,size+size//2+offsetx,2*size-offsety))
    im.paste(bigim,(-size//2-offsetx,-size//2+offsety))
    img.paste(im)
    
def listener():
    global minx, miny, d, dx, dy, curi, curj
    try:
        job=done.get_nowait()
        griddata[job[3]]=Image.fromarray(job[0],mode='L')
        #print(griddata.keys())
        print(job[4])
        #griddata[job[3]].show()
        #print(job[1],job[2],job[3])
        if (0 <= job[3][0]-curi <= 2 or 0 <= job[3][1]-curj <= 2) and nodrag:
            update(dx,dy)
    except: pass
    root.after(20,listener)

if __name__=='__main__':
    size=700
    jobs=mp.Queue()
    done=mp.Queue()
    griddata={}
    grid=[]
    zeroimg=Image.new('L',(size//2,size//2))
    minx, miny = -2,-2
    d=4
    reset()
    procs = [mp.Process(target=worker,args=(jobs,done),daemon=True) for i in range(4)]
    for proc in procs: proc.start()
    root = Tk()
    canv = Canvas(root,width=size,height=size)
    canv.pack()
    bigim=Image.new('L',(size*2,size*2))
    im=Image.new('L',(size,size))
    img=ImageTk.PhotoImage('L',(size,size))
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
