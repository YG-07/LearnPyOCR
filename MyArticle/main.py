#-*- coding:utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import *
from tkinter import messagebox

import os
import  shutil

import time
from selenium import webdriver
from urllib import parse

import pytesseract as pt
from PIL import Image, ImageGrab

import json

class Application(Frame):
    # 一个经典的GUI程序
    def __init__(self, master=None):
        #super()是父类的构造器
        super().__init__(master)
        self.master = master
        self.createState()
        self.master.minsize(self.wmin,self.hmin)
        self.master.resizable(0,0)
        self.pack()
        self.master.update()
        print('当前窗口1：', self.master.winfo_width(), 'x', self.master.winfo_height())
        self.createWidget()
        # self.initFunc()

    # 创建静态数据
    def createState(self):
        # 窗口大小
        self.wmin=700
        self.hmin=200
        self.hp2=550
        self.wp3=910

        # [帮助]菜单
        # ocrdata目录
        self.tessPath = self.splitPath('where tesseract')
        self.tessDataPath = self.tessPath + '\\tessdata'
        self.tessExe = self.tessPath + '\\tesseract.exe'
        pt.pytesseract.tesseract_cmd = self.tessExe
        # 已经安装的语言包
        self.ocrFiles = self.findFile()
        # 根据遍历ocr名生成标签
        with open('./MyOcr.json', 'r', encoding='utf-8') as f:
            self.allOcr = json.load(f)
        print(self.allOcr)

        # 遍历生成语言包字典
        self.ocr = StringVar()
        self.ocrFor = {}
        fla=True
        for key in self.ocrFiles:
            if fla:
                self.ocr.set(key)
                fla=False
            try:
                tmp = self.allOcr[key]
            except KeyError:
                tmp = key + '?'
            self.ocrFor[key] = tmp
        print(self.ocrFor)

        # 单选标签
        self.lang = IntVar()
        self.lang.set(0)
        self.langTxt=['中->英','中->日','英->中','英->日','日->中','日->英']
        self.webTxt=['百度','有道']
        # 翻译对照
        self.baiduTrans={'中':'zh', '英':'en', '日':'jp'}
        self.youdaoTrans=[2, 2, 3, 3, 5, 5]

        # 字体
        self.f1='幼圆 13'
        self.f2='幼圆 12'

        # 控制面板的参数
        self.importFile=None
        self.pwFlag=False
        self.p2Flag=False
        self.fxw=82*12
        self.fxw2=52*12
        self.fxh=24*12
        self.tipFlag=True

        # 路径和网站
        # 翻译网站
        self.transUrl=['','https://fanyi.baidu.com/','http://fanyi.youdao.com/']

        # https://tesseract-ocr.github.io/tessdoc/Data-Files
        self.downOcrUrl='https://github.com/tesseract-ocr/tessdata_fast'
        self.tessdocUrl='https://tesseract-ocr.github.io/tessdoc/'
        self.pytessUrl='https://pypi.org/project/pytesseract/'

        # 爬虫相关
        self.driver = webdriver.PhantomJS(executable_path='./phantomjs.exe')


    # 创建组件
    def createWidget(self):
        # 创建主菜单
        menubar = Menu(self)

        # 创建子菜单,tearoff为0关闭工具栏
        mFile = Menu(menubar, tearoff=0)
        mEdit = Menu(menubar, tearoff=0)
        mTool = Menu(menubar, tearoff=0)
        mHelp = Menu(menubar, tearoff=0)

        # 加入主菜单
        menubar.add_cascade(label='文件(F)', menu=mFile)
        menubar.add_cascade(label='编辑(E)', menu=mEdit)
        menubar.add_cascade(label='工具(T)', menu=mTool)
        menubar.add_cascade(label='帮助(H)', menu=mHelp)

        # 1.添加[文件]的子菜单项
        mFile.add_command(label='导入图片', accelerator='Ctrl+N', command=self.openImg)
        mFile.add_command(label='导入文本', accelerator='Ctrl+O', command=self.openTxt)
        mFile.add_separator()
        mFile.add_command(label='保存识别文本', accelerator='Ctrl+F1', command='')
        mFile.add_command(label='保存翻译文本', accelerator='Ctrl+F2', command='')
        mFile.add_command(label='保存全部', accelerator='Ctrl+S', command='')
        mFile.add_separator()
        mFile.add_command(label='重启', accelerator='Ctrl+R', command='')
        mFile.add_command(label='退出', accelerator='Alt+F4', command='')

        # 2.添加[编辑]的子菜单项
        mEdit.add_command(label='编辑图片', accelerator='Ctrl+M', command='')
        mEdit.add_command(label='编辑文本', accelerator='Ctrl+T', command='')
        mEdit.add_command(label='格式化', accelerator='Ctrl+F', command='')
        mEdit.add_command(label='打开图片目录', command='')
        mEdit.add_command(label='打开文本目录', command='')


        # 3.添加[工具]的子菜单项
        # 3.1二级菜单[切换翻译语言]
        self.mLang = Menu(self, tearoff=0)

        for index, value in enumerate(self.langTxt):
            self.mLang.add_radiobutton(label=value, value=index, variable=self.lang, command=self.chgLang)

        mTool.add_cascade(label='切换翻译语言', menu=self.mLang)
        # 3.2 二级菜单[切换翻译网站]
        self.web = IntVar()
        self.web.set(1)
        mWeb = Menu(self, tearoff=0)
        mWeb.add_radiobutton(label='百度翻译', value=1, variable=self.web, command=self.chgWeb)
        mWeb.add_radiobutton(label='有道翻译', value=2, variable=self.web, command=self.chgWeb)
        mTool.add_cascade(label='切换翻译网站', menu=mWeb)
        mTool.add_command(label='一键截图', accelerator='F2', command=self.grabImg)
        mTool.add_command(label='一键翻译', accelerator='F3', command=self.trans)
        mTool.add_separator()

        self.mOcr = Menu(self, tearoff=0)
        for key in self.ocrFor:
            self.mOcr.add_radiobutton(label=self.ocrFor[key], value=key, variable=self.ocr, command=self.chgOcr)

        mTool.add_cascade(label='切换识别语言', menu=self.mOcr)
        mTool.add_command(label='添加识别语言', command=self.addOcr)

        # 4.添加[帮助]的子菜单项
        mHelp.add_command(label='关于', accelerator='Ctrl+H', command=self.about)
        mHelp.add_separator()
        mHelp.add_command(label='打开OCR安装目录', command=self.openOcrPath)
        mHelp.add_command(label='下载扩展语言识别包', command=self.openOcrWeb)
        mHelp.add_separator()
        mHelp.add_command(label='tessdoc官方文档', command=self.openTessWeb)
        mHelp.add_command(label='pytesseract官方文档', command=self.openPyTessWeb)

        # 将菜单添加到主窗口
        self.master.config(menu=menubar)
        self.menubar = menubar

        # 设计界面和组件
        # 划分面板上下2个面板，设置状态栏
        self.pw = tk.PanedWindow(self.master, height=150, orient='vertical', sashrelief='sunken')
        self.pw.pack(fill='both', expand=1)
        self.p1 = tk.PanedWindow(self.pw, orient='horizontal', sashrelief='sunken')
        self.pw.add(self.p1)
        self.top_frame=ttk.Frame(self.p1, height=150, relief='flat')
        self.p1.add(self.top_frame)

        self.p2 = tk.PanedWindow(self.pw, orient='horizontal', sashrelief='sunken')
        self.left_frame = ttk.Frame(self.p2, height=300, relief='flat')
        self.right_frame = ttk.Frame(self.p2, width=int(self.master.winfo_width()/2), relief='flat')

        # 设置状态栏
        Separator(self.master).pack(fill='x', padx=5)
        status_frame = Frame(self.master, relief='raised').pack(fill='x')
        Label(status_frame, text='状态栏').pack(side='left', fill='x')
        # ttk.Sizegrip(status_frame).pack(anchor='ne')

        # 添加组件
        # 面板1的4个组件
        self.showBtn0 = tk.Button(self.top_frame, width=4, text='展开', font=self.f2)
        self.showBtn0.pack(side='left', padx=2)
        Label(self.top_frame, text='图片路径:', font=self.f2).pack(side='left', padx=2, pady=30)
        self.pathEntry = Entry(self.top_frame, width=40, font=('黑体', 11))
        self.pathEntry.pack(side='left', padx=2)
        self.startBtn = tk.Button(self.top_frame, width=10, text='导入并识别', font=self.f2)
        self.startBtn.pack(side='left', padx=5)
        self.grabBtn = tk.Button(self.top_frame, width=14, text='截图并识别(F2)', font=self.f2)
        self.grabBtn.pack(side='left', padx=2)
        self.resetBtn = tk.Button(self.top_frame, width=14, text='重置', font=self.f2)

        # 面板2的[左框架]组件
        self.editImgBtn = tk.Button(self.left_frame, width=8, text='编辑图片', font=self.f2)
        self.editImgBtn.grid(row=0, column=0, sticky='nw')
        self.formatBtn = tk.Button(self.left_frame, width=6, text='格式化', font=self.f2)
        self.formatBtn.grid(row=0, column=1, sticky='nw')

        self.mOcrMenu = tk.Menubutton(self.left_frame, text='中文(简)', font=self.f2)
        self.mOcrRad = Menu(self.mOcrMenu, tearoff=0)

        for key in self.ocrFor:
            self.mOcrRad.add_radiobutton(label=self.ocrFor[key], value=key, variable=self.ocr, command=self.chgOcr)

        self.mOcrMenu.config(menu=self.mOcrRad)
        self.mOcrMenu.grid(row=0, column=2, sticky='nw')

        self.transBtn = tk.Button(self.left_frame, width=12, text='一键翻译(F3)', font=self.f2, command=self.trans)
        self.transBtn.grid(row=0, column=3, sticky='nw')
        self.showBtn = tk.Button(self.left_frame, width=4, text='展开', font=self.f2)
        self.showBtn.grid(row=0, column=4, columnspan=2, sticky='nw')

        # 文本区1和滚动条，双向绑定
        self.T1 = Text(self.left_frame, width=82, font=('宋体', 12))
        self.t1Bar = ttk.Scrollbar(self.left_frame)
        self.T1.config(yscrollcommand=self.t1Bar.set)
        self.t1Bar.config(command=self.T1.yview)
        self.T1.grid(pady=5, padx=5, row=1, columnspan=5)
        self.t1Bar.grid(row=1, column=5, sticky='ns')

        # 面板2的[右框架]组件
        Label(self.right_frame, text='切换语言:', font='幼圆 12').grid(pady=2,row=0, column=0, sticky='nw')
        self.mLangMenu = tk.Menubutton(self.right_frame, text='中->英', font=self.f2)
        self.mLangRad = Menu(self.mLangMenu, tearoff=0)

        for index, value in enumerate(self.langTxt):
            self.mLangRad.add_radiobutton(label=value, value=index, variable=self.lang, command=self.chgLang)

        self.mLangMenu.config(menu=self.mLangRad)
        self.mLangMenu.grid(row=0, column=1, sticky='nw')

        Label(self.right_frame, text='切换翻译网站:', font=self.f2).grid(pady=2,row=0, column=2, sticky='nw')
        self.mWebMenu = tk.Menubutton(self.right_frame, text='百度', font=self.f2)
        self.mWebRad = Menu(self.mWebMenu, tearoff=0)
        self.mWebRad.add_radiobutton(label='百度', value=1, variable=self.web, command=self.chgWeb)
        self.mWebRad.add_radiobutton(label='有道', value=2, variable=self.web, command=self.chgWeb)
        self.mWebMenu.config(menu=self.mWebRad)
        self.mWebMenu.grid(row=0, column=3, sticky='nw')
        self.webLabel = tk.Label(self.right_frame, text='百度翻译', font=self.f2, fg='blue')
        self.webLabel.grid(pady=2,row=0, column=4, columnspan=2, sticky='nw')

        # 文本区2和滚动条，双向绑定
        self.T2 = Text(self.right_frame, width=52, font=('宋体', 12))
        self.t2Bar = ttk.Scrollbar(self.right_frame)
        self.T2.config(yscrollcommand=self.t2Bar.set)
        self.t2Bar.config(command=self.T2.yview)
        self.T2.grid(pady=5, padx=5, row=1, columnspan=5)
        self.t2Bar.grid(row=1, column=5, sticky='ns')

        # 组件绑定事件
        self.showBtn0.bind('<Button-1>', self.chgPw)
        self.startBtn.bind('<Button-1>', self.start)
        self.grabBtn.bind('<Button-1>', self.grabStart)
        self.showBtn.bind('<Button-1>', self.chgP2)
        self.formatBtn.bind('<Button-1>', self.formatTxt)
        self.editImgBtn.bind('<Button-1>', self.editFile)
        self.resetBtn.bind('<Button-1>', self.resetApp)

        # 全局监听快捷键
        # 1.[文件]菜单
        self.master.bind('<Control-n>', lambda event: self.openImg(event))
        self.master.bind('<Control-o>', lambda event: self.openTxt(event))
        self.master.bind('<Control-F1>', lambda event: self.saveT1(event))
        self.master.bind('<Control-F2>', lambda event: self.saveT2(event))
        self.master.bind('<Control-s>', lambda event: self.saveTxt(event))
        self.master.bind('<Control-r>', lambda event: self.resetApp(event))

        # 2.[编辑]菜单
        self.master.bind('<Control-m>', lambda event: self.editImg(event))
        self.master.bind('<Control-t>', lambda event: self.editTxt(event))

        # 3.[格式]菜单
        self.master.bind('<Control-d>', lambda event: self.fontTxt(event))
        self.master.bind('<Control-f>', lambda event: self.formatTxt(event))

        # 4.[工具]菜单
        self.master.bind('<KeyPress-F2>', lambda event: self.grabImg())
        self.master.bind('<KeyPress-F3>', lambda event: self.trans(event))

        # 5.[帮助]菜单
        self.master.bind('<Control-h>', lambda event: self.about(event))

        # 隐藏快捷键
        # 打开翻译网站
        self.webLabel.bind('<Button-1>', self.openTransUrl)
        # T1、T2字体快捷键
        self.T1.bind('<Control-plus>', lambda event: self.chgFont(event,True))
        self.T1.bind('<Control-minus>', lambda event: self.chgFont(event,False))
        self.T2.bind('<Control-plus>', lambda event: self.chgFont(event,True))
        self.T2.bind('<Control-minus>', lambda event: self.chgFont(event,False))

    # 功能初始化
    # def initFunc(self):
        # if self.importFile==None:
        #     self.menubar.entryconfig('保存识别文本', state='disabled')
        #     self.menubar.entryconfig('保存翻译文本', state='disabled')
        #     self.menubar.entryconfig('保存全部', state='disabled')

    # 事件和函数
    # 分割主面板pw
    def chgPw(self, event=None):
        if not self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hp2))
            self.master.minsize(self.wmin, self.hp2)
            self.startBtn.pack_forget()
            self.grabBtn.pack_forget()
            self.resetBtn.pack(side='left', padx=2)
            self.showBtn0['text'] = '收起'
            self.pw['height'] = 450
            self.pw.add(self.p2)
            self.p2.add(self.left_frame)
        elif self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hmin))
            self.master.minsize(self.wmin, self.hmin)
            self.resetBtn.pack_forget()
            self.startBtn.pack(side='left', padx=5)
            self.grabBtn.pack(side='left', padx=5)
            self.showBtn0['text'] = '展开'
            self.pw['height'] = 150
            self.pw.forget(self.p2)
        self.pwFlag = not self.pwFlag
        self.master.update()
        print('ok,当前窗口2：', self.master.winfo_width(), 'x', self.master.winfo_height())

    # 分割2面板p2
    def chgP2(self, event=None):
        resfont = self.T1['font'].split(' ')
        tmp = int(resfont[1])
        if not self.p2Flag:
            self.master.geometry('{0}x{1}'.format(self.wp3,self.hp2))
            self.master.minsize(self.wp3, self.hp2)
            self.T1['width'] = 52
            self.showBtn['text'] = '收起'
            self.p2.forget(self.left_frame)
            self.left_frame['width']=450
            self.p2.add(self.left_frame)
            self.p2.add(self.right_frame)
            self.T1['width'] = int(self.fxw2 / tmp) - 2
        else:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hp2))
            self.master.minsize(self.wmin, self.hp2)
            self.T1['width'] = 82
            self.showBtn['text'] = '展开'
            self.p2.forget(self.right_frame)
            self.T1['width'] = int(self.fxw / tmp) - 2
            self.T1['height'] = int(self.fxh / tmp)
        self.p2Flag = not self.p2Flag
        self.master.update()

    # 1.[开始识别]按钮的事件
    def start(self, event=None):
        path=askopenfilename(title='导入图片或文本文件', filetypes=[('所有文件', '*.*'),('文本文件', '.txt')])
        if path:
            (dir,file)=os.path.split(path)
            (filename,extension)=os.path.splitext(file)
            print(path,extension)
            if extension=='.txt':
                self.importFile=path
                self.editImgBtn['text']='编辑文本'
                self.chgPw()
                with open(path, 'r') as f:
                    text=f.read()
                self.T1.delete(1.0, END)
                self.T1.insert(1.0, text)
            else:
                try:
                    self.importFile=path
                    self.chgPw()
                    img = Image.open(path)
                    text = pt.image_to_string(img, lang=self.ocr.get())
                    self.T1.delete(1.0, END)
                    self.T1.insert(1.0, text)
                    print(text)
                except:
                    messagebox.showerror('导入错误', '导入文件格式错误，不是图片或文本!')

    # 2.[截图并识别]按钮的事件
    def grabStart(self, event=None):
        if (self.pwFlag==False) and (self.p2Flag==False):
            print('一键截图')
            self.grabImg(self)

            # self.chgPw()

    # 快捷键和菜单事件处理函数
    # 1.[文件]菜单
    # 1.导入图片
    def openImg(self, event=None):
        self.start(self)
        print('导入图片')

    # 2.打开文本
    def openTxt(self, event=None):
        self.start(self)
        print('打开文本')

    # 3.保存识别文本
    def saveT1(self, event=None):
        print('保存识别文本')

    # 4.保存翻译文本
    def saveT2(self, event=None):
        print('保存翻译文本')

    # 5.保存合并2个文本
    def saveTxt(self, event=None):
        print('保存合并2个文本')

    # 6.重启
    def resetApp(self, event=None):
        print('重启')

    # 2.[编辑]菜单
    # 1.编辑图片
    def editImg(self, event=None):
        print('编辑图片')

    # 2.编辑文本
    def editTxt(self, event=None):
        print('编辑文本')

    def editFile(self, event=None):
        if self.importFile:
            os.startfile(self.importFile)
        else:
            messagebox.showinfo('信息', '未打开任何文件！')

    # 3.打开图片地址
    def openImgPath(self, event=None):
        print('打开图片地址')

    # 4.打开文本地址
    def openTxtPath(self, event=None):
        print('打开文本地址')

    # 3.[格式]菜单
    # 1.字体
    def fontTxt(self, event=None):
        print('字体')

    # 2.格式化
    def formatTxt(self, event=None):
        txt = self.T1.get(1.0, END)
        txt = txt.replace('  ', ' ')
        txt =txt.replace('\r','\n')
        txt =txt.replace('\n\n','\n')
        txt =txt.replace('\n ','')
        txt =txt.replace('',' ')
        self.T1.delete(1.0, END)
        self.T1.insert(1.0, txt)
        txt = self.T2.get(1.0, END)
        txt = txt.replace('  ', ' ')
        txt = txt.replace('\r', '\n')
        txt = txt.replace('\n\n','\n')
        txt = txt.replace('\n ', '')
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, txt)

    # 4.[工具]菜单
    # 1.切换识别语言
    def chgOcr(self, event=None):
        self.mOcrMenu['text'] = self.ocrFor[self.ocr.get()]

    # 2.添加识别语言
    def aliasOk(self, filename, event=None):
        self.aliasname = self.alEntry.get()
        self.aliasname = self.aliasname.replace(' ', '')
        if self.aliasname:
            self.allOcr[filename] = self.aliasname
            with open('./MyOcr.json', 'w', encoding='utf-8') as f:
                ocrStr = json.dumps(self.allOcr).encode('utf-8').decode('unicode-escape')
                print(ocrStr)
                f.write(ocrStr)
            self.aliasWin.destroy()
        else:
            messagebox.showinfo('提示', '语音包别名错误！')

    def addOcr(self, event=None):
        print('添加识别语言')
        addPath = askopenfilename(title='添加traineddata文件到tessdata目录', filetypes=[('OCR文件', '.traineddata')])
        if addPath:
            file=addPath.split('/')[-1]
            (filename, extension) = os.path.splitext(file)
            dst=self.tessDataPath+'\\'+file
            print(addPath, dst)
            flag=False
            if os.path.exists(dst):
                if messagebox.askquestion('信息', filename+'语言包已经存在！是否替换？')=='yes':
                    flag=True
                    print(flag)
            else:
                flag=True
            if flag:
                shutil.copyfile(addPath, dst)
                messagebox.showinfo('信息', '成功添加'+filename+'语言包！重启软件生效!')
                self.aliasWin = tk.Toplevel()
                self.aliasWin.geometry('270x70+400+200')
                self.aliasWin.title('设置语言包别名')
                self.alEntry = Entry(self.aliasWin, width=20)
                self.alEntry.pack(pady=5)
                self.alBtn1 = Button(self.aliasWin, text='确定', width=5)
                self.alBtn1.pack(side='left', padx=60)
                self.alBtn2 = Button(self.aliasWin, text='取消', width=5)
                self.alBtn2.pack(side='left')
                self.alBtn1.bind('<Button-1>', lambda event: self.aliasOk(filename))
                self.alBtn2.bind('<Button-1>', lambda event: self.aliasWin.destroy())
                self.aliasWin.mainloop()

    # 3.一键截图
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
        if len(self.r)>0:
            self.c.create_rectangle(self.r[0], self.r[1], self.r[2], self.r[3], outline='#fff')
            self.r = []
        self.r.append(self.sx)
        self.r.append(self.sy)
        self.r.append(event.x)
        self.r.append(event.y)
        self.startLine = False
        self.lastDraw = 0
    #
    def grabSave(self):
        self.gWin.destroy()
        self.imgTmp = ImageGrab.grab(bbox=(self.r[0], self.r[1], self.r[2], self.r[3]))
        self.imgTmp.save('grab.jpg')

    # 矩形
    def myRect(self, event):
        self.startDraw(event)
        self.lastDraw=self.c.create_rectangle(self.sx, self.sy, event.x, event.y, outline='#777')


    def grabImg(self, event=None):
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
        self.gWin.attributes('-alpha', 0.4)
        self.gWin.geometry('{0}x{1}+0+0'.format(w, h))
        self.gWin.resizable(0, 0)
        self.c=Canvas(self.gWin, width=w, height=h)
        self.c.pack()
        self.gWin.bind('<KeyPress-Escape>', lambda event: self.gWin.destroy())
        self.c.bind('<B1-Motion>', self.myRect)
        self.c.bind('<ButtonRelease-1>', self.stopDraw)
        self.gWin.bind('<KeyPress-Return>', lambda event: self.grabSave())

        self.gWin.mainloop()

    # 4.一键翻译
    def baiduTransMain(self, event=None):
        print('百度翻译')
        txt = self.T1.get(1.0, END)
        txt.replace('\n', '')
        ll = self.langTxt[self.lang.get()]
        (l1, l2) = ll.split('->')
        print(txt, self.baiduTrans[l1], self.baiduTrans[l2])
        url = self.transUrl[self.web.get()] + '#{0}/{1}/{2}'\
            .format(self.baiduTrans[l1], self.baiduTrans[l2],parse.quote(txt))
        print(url)
        self.driver.get(url)
        time.sleep(0.6)
        self.driver.save_screenshot("trans.png")
        finds = self.driver.find_elements_by_xpath('//*[@class="output-bd"]/p/span')
        word = ''
        for item in finds:
            word += item.text + '\n'
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, word)

    def youdaoTransMain(self, event=None):
        print('有道翻译')
        txt = self.T1.get(1.0, END)
        txt.replace('\n', '')
        self.driver.get(self.transUrl[self.web.get()])
        time.sleep(0.3)
        self.driver.find_element_by_xpath('//*[@id="langSelect"]/span').click()
        time.sleep(0.1)
        self.driver.find_element_by_xpath('//*[@id="languageSelect"]/li[{0}]/a'.format(self.youdaoTrans[self.lang.get()])).click()
        time.sleep(0.1)
        self.driver.find_element_by_id('inputOriginal').send_keys(txt)
        time.sleep(0.2)
        self.driver.find_element_by_id('transMachine').click()
        time.sleep(0.5)
        self.driver.save_screenshot("trans.png")
        finds = self.driver.find_elements_by_xpath('//*[@id="transTarget"]/p/span')
        word = ''
        for item in finds:
            word += item.text + '\n'
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, word)

    def trans(self, event=None):
        if self.pwFlag:
            if self.p2Flag == False:
                self.chgP2()
            if self.web.get()==1:
                self.baiduTransMain()
            else:
                self.youdaoTransMain()


    # 5.切换语言
    def chgLang(self, event=None):
        # print('切换语言',self.langTxt[self.lang.get()])
        self.mLangMenu['text']=self.langTxt[self.lang.get()]


    # 6.切换网站
    def chgWeb(self, event=None):
        if self.tipFlag:
            self.tipFlag = False
            messagebox.showinfo('提示', '有道翻译的"英<->日"互译不可用')
        self.mWebMenu['text'] = self.webTxt[self.web.get()]
        self.webLabel['text'] = self.webTxt[self.web.get()]+'翻译'

    # 7.打开翻译网站
    def openTransUrl(self, event=None):
        os.startfile(self.transUrl[self.web.get()])

    # 5.[帮助]菜单
    # 1.关于
    def about(self, event=None):
        aboutWin = tk.Toplevel()
        aboutWin.title('帮助和关于')
        aboutWin.geometry('400x300+500+200')
        aboutWin.resizable(0,0)
        l = tk.Label(aboutWin, text='Python的图片文字识别的Tkinter程序', font=('微软雅黑',16))
        l.pack(anchor='w',padx=20, pady=10)
        Separator(aboutWin).pack(fill='x', padx=5)
        aboutTxt = '这是关于内容\n' \
                   '哈哈哈'
        helpTxt = '这是帮助内容\n' \
                  '喵喵喵\n' \
                  '嘤嘤嘤\n'
        tk.Label(aboutWin, text='关于', font=('微软雅黑',13)).pack(anchor='w',padx=40, pady=5)
        aboutLabel = tk.Label(aboutWin, text=aboutTxt, font=('宋体',11), justify='left')
        aboutLabel.pack(anchor='w',padx=50)
        tk.Label(aboutWin, text='帮助', font=('微软雅黑', 13)).pack(anchor='w', padx=40, pady=5)
        helpLabel = tk.Label(aboutWin, text=helpTxt, font=('宋体', 11), justify='left')
        helpLabel.pack(anchor='w',padx=50)
        tk.Label(aboutWin, text='Copyright © 2020-2021 Siwei Du. All rights reserved.', font=('黑体', 10)).pack(anchor='s', pady=20)
        aboutWin.mainloop()

    # 通过cmd获取路径
    def splitPath(self, cmd):
        path = os.popen(cmd).read()
        tmp = path.split('\\')
        tmp.pop()
        path = '\\'.join(tmp)
        # print(path)
        return path

    # 2.打开OCR目录
    def openOcrPath(self, event=None):
        print('打开OCR目录',self.tessPath)
        path = self.tessPath
        os.startfile(path)

    # 3.下载扩展语言识别包
    def openOcrWeb(self, event=None):
        os.startfile(self.downOcrUrl)

    # 4.打开tessdoc官方文档
    def openTessWeb(self, event=None):
        os.startfile(self.tessdocUrl)

    # 5.打开pytessract官方文档
    def openPyTessWeb(self, event=None):
        os.startfile(self.pytessUrl)

    # 其他快捷键事件处理函数
    # 1.遍历文件夹，获取指定后缀文件
    def findFile(self):
        items = os.listdir(self.tessDataPath)
        newList=[]
        for item in items:
            if item.endswith('.traineddata'):
                (filename,extension)=os.path.splitext(item)
                newList.append(filename)
        print(newList)
        return newList
    # 1.文本域的字体+-
    def chgFont(self, event, bool, dlt=1):
        print(event)
        resfont = event.widget['font'].split(' ')
        tmp = int(resfont[1])
        if bool:
            if(tmp+dlt<=30):
                tmp+=dlt
            else:
                tmp=30
        else:
            if(tmp-dlt>=10):
                tmp-=dlt
            else:
                tmp=10
        resfont[1] = str(tmp)
        resfont = ' '.join(resfont)
        event.widget['font'] = resfont
        tw = event.widget['height']
        print(tw)
        if self.p2Flag:
            event.widget['width'] = int(self.fxw2 / tmp) - 2
        else:
            event.widget['width'] = int(self.fxw / tmp) - 2
        event.widget['height'] = int(self.fxh / tmp)
        # 推理：文本域动态宽度 82*12=fxw   ?*13=fxw    ?*14=fxw

if __name__ == '__main__':
    root = Tk()
    root.title('图片文字识别程序')
    root.geometry('700x200+200+160')
    app = Application(master=root)
    root.update()
    root.mainloop()