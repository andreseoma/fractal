from tkinter import *
from tkinter import ttk
from math import copysign
from time import time


def iterate(c,n):
    z=0
    for n in range(n):
        z=z*z+c
        if abs(z)>=2: return 255-n
    return 0
            
def image(z0,z1,px,py):
    stepx=(z1-z0).real/px
    stepy=(z0-z1).imag/py
    img=''
    for y in range(py):
        rida=''
        for x in range(px):
            z=z0+x*stepx-(y*stepy)*1j
            col=iterate(z,200)
            rida+='#%02x%02x%02x ' % (col,col,col)
        img+='{'+rida+'} '
    return img

def hit(event):
    global start
    start=(event.x, event.y)
    img.put('{red red red}')

def drag(event):
    global start
    global x
    global y
    change=min(abs(start[0]-event.x),abs(start[1]-event.y))
    x=start[0]+copysign(change,event.x-start[0])
    y=start[1]+copysign(change,event.y-start[1])
    canv.coords(rect,start[0],start[1],x,y)
    canv.itemconfig(rect,state='normal')

def drop(event):
    global start
    global z1
    global z2
    canv.itemconfig(rect,state='hidden')
    if start==(event.x,event.y):
        return
    z1,z2=z1+start[0]/300*(z2-z1).real+start[1]/300*(z2-z1).imag*1j,\
    z1+x/300*(z2-z1).real+y/300*(z2-z1).imag*1j
    
    if z1.real>z2.real: z1,z2=z2,z1
    if z1.imag<z2.imag: z1,z2=z1.real+z2.imag*1j, z2.real+z1.imag*1j
    tim=time()
    frac=image(z1,z2,300,300)
    print(time()-tim)
    img.put(frac)
    canv.itemconfig(imag,image=img)
    print(z1,z2,z1-z2)

z1=-2.2+2j
z2=1.8-2j
root = Tk()
canv = Canvas(root,width=300,height=300)
canv.pack()
img = PhotoImage(width=300,height=300)
print(1)
frac=image(z1,z2,300,300)
print(2)
img.put(frac)
imag=canv.create_image(0,0,image=img,anchor='nw')
rect=canv.create_rectangle(50,50,200,200,state='hidden')
canv.bind('<Button-1>', hit)
canv.bind('<B1-Motion>', drag)
canv.bind('<ButtonRelease>',drop)
root.mainloop()
