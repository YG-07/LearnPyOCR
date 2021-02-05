#-*- coding:utf-8 -*-


import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *

import os
import  shutil

from PIL import Image, ImageGrab


class Application(Frame):
    # 一个经典的GUI程序
    def __init__(self, master=None):
        super().__init__(master)    #super()是父类的构造器
        self.master = master
        self.pack()

        self.createWidget()

    def createWidget(self):
        # 创建组件
        self.btn=Button(self, text='一键截图(F2)')
        self.btn.pack()

        self.btn.bind('<Button-1>', self.btnGrabImg)
        self.master.bind('<KeyPress-F2>', self.grabImg)

    # 3.一键截图
    def grabImg(self, event=None):
        self.master.state('icon')
        self.btnGrabImg()

    # 初始化数据
    def createData(self):
        self.sx = 0
        self.sy = 0
        self.r = []
        self.lastDraw = 0
        self.startLine = False
        self.pastDraw = None

    # 画图开始函数
    def startDraw(self, event):
        self.c.delete(self.lastDraw)
        if not self.startLine:
            self.startLine = True
            self.sx = event.x
            self.sy = event.y

    # 画图结束
    def stopDraw(self, event):
        print('坐标：({0},{1})-({2},{3})'.format(self.sx, self.sy, event.x, event.y))
        print(self.r)
        if len(self.r) > 0:
            self.c.create_rectangle(self.r[0], self.r[1], self.r[2], self.r[3], outline='#fff')
            self.r = []
        self.r.append(self.sx)
        self.r.append(self.sy)
        self.r.append(event.x)
        self.r.append(event.y)
        self.startLine = False
        self.lastDraw = 0

    # 保存图片
    def grabSave(self):
        self.c.create_rectangle(self.r[0], self.r[1], self.r[2], self.r[3], outline='#fff')
        self.gWin.attributes('-alpha', 0)
        self.imgTmp = ImageGrab.grab(bbox=(self.r[0], self.r[1], self.r[2], self.r[3]))
        self.imgTmp.save('grab.jpg')
        self.gWin.destroy()

    # 矩形
    def myRect(self, event):
        self.startDraw(event)
        self.lastDraw = self.c.create_rectangle(self.sx, self.sy, event.x, event.y, outline='#000')

    def btnGrabImg(self, event=None):
        from win32 import win32api, win32gui,win32print
        import win32con
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
        print('当前分辨率：',w,'x',h)

        self.createData()
        self.gWin = tk.Toplevel()
        self.gWin.title(' ')
        self.gWin.overrideredirect(True)
        self.gWin.attributes('-alpha', 0.5)
        self.gWin.geometry('{0}x{1}+0+0'.format(w, h))
        self.gWin.resizable(0, 0)
        self.c=Canvas(self.gWin, width=w, height=h)
        self.c.pack()
        self.gWin.bind('<KeyPress-Escape>', lambda event: self.gWin.quit())
        self.c.bind('<B1-Motion>', self.myRect)
        self.c.bind('<ButtonRelease-1>', self.stopDraw)
        self.gWin.bind('<KeyPress-Return>', lambda event: self.grabSave())

        self.gWin.mainloop()



if __name__ == '__main__':
    root = Tk()
    root.title('一个经典的面向对象的GUI程序')
    root.geometry('20x30+400+160')
    app = Application(master=root)
    root.mainloop()