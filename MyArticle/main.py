#-*- coding:utf-8 -*-

import os
import shutil

from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox

from time import sleep

from selenium.webdriver import PhantomJS
from urllib.parse import quote

from pytesseract.pytesseract import tesseract_cmd, image_to_string
from PIL import Image
from PIL.ImageGrab import grab

from json import load, dumps
from win32api import GetSystemMetrics


class Application(Frame):
    # 经典的GUI程序模式
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

    # 一、创建静态数据
    def createState(self):
        # 一、静态数据
        # 1.窗口大小、字体
        self.wmin = 700
        self.hmin = 200
        self.hp2 = 550
        self.wp3 = 910
        self.f1 = '幼圆 13'
        self.f2 = '幼圆 12'
        # 2.翻译语言汇总和对照表
        self.langTxt = ['中->英', '中->日', '英->中', '英->日', '日->中', '日->英']
        self.webTxt = ['百度', '有道']
        self.baiduTrans = {'中': 'zh', '英': 'en', '日': 'jp'}
        self.youdaoTrans = [2, 2, 3, 3, 5, 5]
        self.transUrl = ['https://fanyi.baidu.com/', 'http://fanyi.youdao.com/']
        # 3.相关网站
        self.downOcrUrl = 'https://github.com/tesseract-ocr/tessdata_fast'
        self.tessdocUrl = 'https://tesseract-ocr.github.io/tessdoc/'
        self.pytessUrl = 'https://pypi.org/project/pytesseract/'
        # (未使用)语言包介绍： https://tesseract-ocr.github.io/tessdoc/Data-Files
        # 4.爬虫相关路径
        self.driver = PhantomJS(executable_path='./phantomjs.exe')

        # 二、动态数据
        # 1.控制面板的参数
        self.importFile = None
        self.importType = None
        self.pwFlag = False
        self.p2Flag = False
        self.tipFlag = True
        self.fxw = 82 * 12
        self.fxw2 = 52 * 12
        self.fxh = 24 * 12
        # 2.翻译网站变量
        self.web = IntVar()
        self.web.set(0)
        # 3.翻译语言变量
        self.lang = IntVar()
        self.lang.set(0)
        # 4.文件状态变量
        self.stat = StringVar()
        self.stat.set('欢迎使用！当前未打开文件')
        # 5.设置当前ocr变量
        self.ocr = StringVar()

        # 三、计算后的数据
        # 1.tessOCR相关目录
        self.tessPath = self.splitPath('where tesseract')
        self.tessDataPath = self.tessPath + '\\tessdata'
        tesseract_cmd = self.tessPath + '\\tesseract.exe'

        # 2.获取所有语言包名对照变量allOcr(可以手动修改json,或提供程序添加语言包)
        self.ocrFiles = self.findFile()
        with open('MyOcr.json', 'r', encoding='utf-8') as f:
            self.allOcr = load(f)
        print(self.allOcr)

        # 3.根据allOcr变量(没有的添加?)，生成语言包字典，修改ocr变量
        self.ocrFor = {}
        fla = True
        for key in self.ocrFiles:
            if fla:
                self.ocr.set(key)
                fla = False
            try:
                tmp = self.allOcr[key]
            except KeyError:
                tmp = key + '?'
            self.ocrFor[key] = tmp
        print(self.ocrFor)

    # 二、创建组件
    def createWidget(self):
        # 一、1.创建主菜单
        menubar = Menu(self)

        # 2.创建子菜单,tearoff为0关闭工具栏
        mFile = Menu(menubar, tearoff=0)
        mEdit = Menu(menubar, tearoff=0)
        mTool = Menu(menubar, tearoff=0)
        mHelp = Menu(menubar, tearoff=0)

        # 3.加入主菜单
        menubar.add_cascade(label='文件(F)', menu=mFile)
        menubar.add_cascade(label='编辑(E)', menu=mEdit)
        menubar.add_cascade(label='工具(T)', menu=mTool)
        menubar.add_cascade(label='帮助(H)', menu=mHelp)

        # 二、1.添加[文件]的子菜单项
        mFile.add_command(label='导入图片', accelerator='Ctrl+N', command=self.openImg)
        mFile.add_command(label='导入文本', accelerator='Ctrl+O', command=self.openTxt)
        mFile.add_separator()
        mFile.add_command(label='保存识别文本', accelerator='Ctrl+F1', command=self.saveT1)
        mFile.add_command(label='保存翻译文本', accelerator='Ctrl+F2', command=self.saveT2)
        mFile.add_command(label='保存全部', accelerator='Ctrl+S', command=self.saveTxt)
        mFile.add_separator()
        mFile.add_command(label='重置', accelerator='Ctrl+R', command=self.resetApp)
        mFile.add_command(label='退出', accelerator='Alt+F4', command=lambda : self.master.destroy())

        # 2.添加[编辑]的子菜单项
        mEdit.add_command(label='编辑图片', accelerator='Ctrl+M', command=self.editImg)
        mEdit.add_command(label='编辑文本', accelerator='Ctrl+T', command=self.editTxt)
        mEdit.add_command(label='格式化', accelerator='Ctrl+F', command=self.formatTxt)
        mEdit.add_command(label='打开图片目录', command=self.openImgPath)
        mEdit.add_command(label='打开文本目录', command=self.openTxtPath)

        # 3.添加[工具]的子菜单项
        # 3.1 二级菜单[切换翻译语言]
        self.mLang = Menu(self, tearoff=0)
        for index, value in enumerate(self.langTxt):
            self.mLang.add_radiobutton(label=value, value=index, variable=self.lang, command=self.chgLang)
        mTool.add_cascade(label='切换翻译语言', menu=self.mLang)

        # 3.2 二级菜单[切换翻译网站]
        mWeb = Menu(self, tearoff=0)
        mWeb.add_radiobutton(label='百度翻译', value=0, variable=self.web, command=self.chgWeb)
        mWeb.add_radiobutton(label='有道翻译', value=1, variable=self.web, command=self.chgWeb)
        mTool.add_cascade(label='切换翻译网站', menu=mWeb)
        mTool.add_command(label='一键截图', accelerator='F2', command=self.grabImg)
        mTool.add_command(label='一键翻译', accelerator='F3', command=self.trans)
        mTool.add_separator()

        # 3.3 二级菜单[切换识别语言包]
        self.mOcr = Menu(self, tearoff=0)
        for key in self.ocrFor:
            self.mOcr.add_radiobutton(label=self.ocrFor[key], value=key, variable=self.ocr, command=self.chgOcr)
        mTool.add_cascade(label='切换识别语言', menu=self.mOcr)
        mTool.add_command(label='添加识别语言', command=self.addOcr)

        # 4.添加[帮助]的子菜单项
        mHelp.add_command(label='关于', accelerator='Ctrl+H', command=self.about)
        mHelp.add_separator()
        mHelp.add_command(label='打开OCR安装目录', command=lambda :os.startfile(self.tessPath))
        mHelp.add_command(label='下载扩展语言识别包', command=lambda :os.startfile(self.downOcrUrl))
        mHelp.add_separator()
        mHelp.add_command(label='tessdoc官方文档', command=lambda :os.startfile(self.tessdocUrl))
        mHelp.add_command(label='pytesseract官方文档', command=lambda :os.startfile(self.pytessUrl))

        # 4.1将菜单添加到主窗口
        self.master.config(menu=menubar)
        self.menubar = menubar

        # 三、1.设计界面和组件
        # 1.1划分面板上下2个面板，设置状态栏
        self.pw = PanedWindow(self.master, height=150, orient='vertical', sashrelief='sunken')
        self.pw.pack(fill='both', expand=1)
        self.p1 = PanedWindow(self.pw, orient='horizontal', sashrelief='sunken')
        self.pw.add(self.p1)
        self.top_frame=ttk.Frame(self.p1, height=150, relief='flat')
        self.p1.add(self.top_frame)

        self.p2 = PanedWindow(self.pw, orient='horizontal', sashrelief='sunken')
        self.left_frame = ttk.Frame(self.p2, height=300, relief='flat')
        self.right_frame = ttk.Frame(self.p2, width=int(self.master.winfo_width()/2), relief='flat')

        # 1.2设置状态栏
        ttk.Separator(self.master).pack(fill='x', padx=5)
        self.status_frame = Frame(self.master, relief='raised').pack(fill='x')
        self.state_label = Label(self.status_frame, textvariable=self.stat)
        self.state_label.pack(side='left', fill='x')

        # 四、1.为界面添加组件
        # 1.1面板1的4个组件
        self.showBtn0 = Button(self.top_frame, width=4, text='展开', font=self.f2)
        self.showBtn0.pack(side='left', padx=2)
        Label(self.top_frame, text='图片路径:', font=self.f2).pack(side='left', padx=2, pady=30)
        self.pathEntry = Entry(self.top_frame, width=40, font=('黑体', 11))
        self.pathEntry.pack(side='left', padx=2)
        self.startBtn = Button(self.top_frame, width=10, text='导入并识别', font=self.f2)
        self.startBtn.pack(side='left', padx=5)
        self.grabBtn = Button(self.top_frame, width=14, text='截图并识别', font=self.f2)
        self.grabBtn.pack(side='left', padx=2)
        self.resetBtn = Button(self.top_frame, width=14, text='重置', font=self.f2)
        self.reStartBtn = Button(self.top_frame, width=14, text='刷新', font=self.f2)

        # 1.2面板2的[左框架]组件
        self.editImgBtn = Button(self.left_frame, width=8, text='编辑', font=self.f2)
        self.editImgBtn.grid(row=0, column=0, sticky='nw')
        self.formatBtn = Button(self.left_frame, width=6, text='格式化', font=self.f2)
        self.formatBtn.grid(row=0, column=1, sticky='nw')

        self.mOcrMenu = Menubutton(self.left_frame, text='中文(简)', font=self.f2)
        self.mOcrRad = Menu(self.mOcrMenu, tearoff=0)
        for key in self.ocrFor:
            self.mOcrRad.add_radiobutton(label=self.ocrFor[key], value=key, variable=self.ocr, command=self.chgOcr)
        self.mOcrMenu.config(menu=self.mOcrRad)
        self.mOcrMenu.grid(row=0, column=2, sticky='nw')

        self.transBtn = Button(self.left_frame, width=12, text='一键翻译(F3)', font=self.f2, command=self.trans)
        self.transBtn.grid(row=0, column=3, sticky='nw')
        self.showBtn = Button(self.left_frame, width=4, text='展开', font=self.f2)
        self.showBtn.grid(row=0, column=4, columnspan=2, sticky='nw')

        # 1.3文本区1和滚动条，双向绑定
        self.T1 = Text(self.left_frame, width=82, font=('宋体', 12))
        self.t1Bar = ttk.Scrollbar(self.left_frame)
        self.T1.config(yscrollcommand=self.t1Bar.set)
        self.t1Bar.config(command=self.T1.yview)
        self.T1.grid(pady=5, padx=5, row=1, columnspan=5)
        self.t1Bar.grid(row=1, column=5, sticky='ns')

        # 2.1面板2的[右框架]组件
        Label(self.right_frame, text='切换语言:', font='幼圆 12').grid(pady=2,row=0, column=0, sticky='nw')
        self.mLangMenu = Menubutton(self.right_frame, text='中->英', font=self.f2)
        self.mLangRad = Menu(self.mLangMenu, tearoff=0)

        for index, value in enumerate(self.langTxt):
            self.mLangRad.add_radiobutton(label=value, value=index, variable=self.lang, command=self.chgLang)
        self.mLangMenu.config(menu=self.mLangRad)
        self.mLangMenu.grid(row=0, column=1, sticky='nw')

        Label(self.right_frame, text='切换翻译网站:', font=self.f2).grid(pady=2,row=0, column=2, sticky='nw')
        self.mWebMenu = Menubutton(self.right_frame, text='百度', font=self.f2)
        self.mWebRad = Menu(self.mWebMenu, tearoff=0)
        self.mWebRad.add_radiobutton(label='百度', value=0, variable=self.web, command=self.chgWeb)
        self.mWebRad.add_radiobutton(label='有道', value=1, variable=self.web, command=self.chgWeb)
        self.mWebMenu.config(menu=self.mWebRad)
        self.mWebMenu.grid(row=0, column=3, sticky='nw')
        self.webLabel = Label(self.right_frame, text='百度翻译', font=self.f2, fg='blue')
        self.webLabel.grid(pady=2,row=0, column=4, columnspan=2, sticky='nw')

        # 2.2文本区2和滚动条，双向绑定
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
        self.reStartBtn.bind('<Button-1>', self.startRead)

        # 全局监听快捷键
        # 1.[文件]菜单
        self.master.bind('<Control-n>', self.openImg)
        self.master.bind('<Control-o>', self.openTxt)
        self.master.bind('<Control-F1>', self.saveT1)
        self.master.bind('<Control-F2>', self.saveT2)
        self.master.bind('<Control-s>', self.saveTxt)
        self.master.bind('<Control-r>', self.resetApp)

        # 2.[编辑]菜单
        self.master.bind('<Control-m>', self.editImg)
        self.master.bind('<Control-t>', self.editTxt)
        self.master.bind('<Control-f>', self.formatTxt)

        # 3.[工具]菜单
        self.master.bind('<KeyPress-F2>', self.grabImg)
        self.master.bind('<KeyPress-F3>', self.trans)

        # 4.[帮助]菜单
        self.master.bind('<Control-h>', self.about)

        # 隐藏快捷键
        # 打开翻译网站
        self.webLabel.bind('<Button-1>', self.openTransUrl)
        # T1、T2字体快捷键
        self.T1.bind('<Control-plus>', lambda event: self.chgFont(event,True))
        self.T1.bind('<Control-minus>', lambda event: self.chgFont(event,False))
        self.T2.bind('<Control-plus>', lambda event: self.chgFont(event,True))
        self.T2.bind('<Control-minus>', lambda event: self.chgFont(event,False))

    # 三、事件和函数
    # ***********注释规则：[函数类别序号].[函数序号]-[累加函数个数]***********
    # 1.面板切换操作
    # 1.1-1.分割主面板pw
    def chgPw(self, event=None):
        if not self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hp2))
            self.master.minsize(self.wmin, self.hp2)
            self.startBtn.pack_forget()
            self.grabBtn.pack_forget()
            self.resetBtn.pack(side='left', padx=2)
            self.reStartBtn.pack(side='left', padx=2)
            self.showBtn0['text'] = '收起'
            self.pw['height'] = 450
            self.pw.add(self.p2)
            self.p2.add(self.left_frame)
        elif self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hmin))
            self.master.minsize(self.wmin, self.hmin)
            self.resetBtn.pack_forget()
            self.reStartBtn.pack_forget()
            self.startBtn.pack(side='left', padx=5)
            self.grabBtn.pack(side='left', padx=5)
            self.showBtn0['text'] = '展开'
            self.pw['height'] = 150
            self.pw.forget(self.p2)
        self.pwFlag = not self.pwFlag
        self.master.update()
        print('ok,当前窗口2：', self.master.winfo_width(), 'x', self.master.winfo_height())

    # 1.2-1.分割2面板p2
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

    # 2.面板1事件
    # 2.1-3.[开始识别]按钮的事件
    def start(self, event=None, tit='文件'):
        if tit=='图片':
            ftype=[('JPG文件', '.jpg'), ('PNG文件', '.png'), ('BMP文件', '.bmp'), ('GIF文件', '.gif'),('所有文件', '*.*')]
        elif tit=='文本':
            ftype = [('文本文件', '.txt'),('所有文件', '*.*')]
        else:
            ftype = [('图片/文本文件', '*.*')]

        if self.pwFlag or self.p2Flag:
            if messagebox.askquestion('提示', '是否重置软件?')=='no':
                return
            else:
                self.resetApp()
        path=askopenfilename(title='导入'+tit, filetypes=ftype)
        if path:
            self.resetApp()
            self.importFile = path
            (dir,file)=os.path.split(path)
            (filename,extension)=os.path.splitext(file)
            print(path,extension)
            if extension=='.txt':
                self.chgState(event,'文本')
            else:
                try:
                    self.chgState(event, '图片')
                except:
                    messagebox.showerror('导入错误', '导入文件格式错误，不是图片或文本!')
                    self.stat.set('当前未打开文件')

    # 2.2-4.[截图并识别]按钮的事件
    def grabStart(self, event=None):
        print('一键截图')
        if (self.pwFlag == False) and (self.p2Flag == False):
            self.resetApp()
            self.grabImg('btn')

    # 2.3-5.[刷新]按钮
    def startRead(self, event=None):
        if self.importFile==None:
            return
        elif self.importFile[-3:]=='txt':
            with open(self.importFile, 'r') as f:
                text = f.read()
            self.T1.delete(1.0, END)
            self.T1.insert(1.0, text)
        else:
            img = Image.open(self.importFile)
            text = image_to_string(img, lang=self.ocr.get())
            self.T1.delete(1.0, END)
            self.T1.insert(1.0, text)
            print('图片文字识别成功')

    # 2.4-6.改变状态
    def chgState(self, event=None, type='文本'):
        self.stat.set('当前打开[{0}]文件：'.format(type) + self.importFile)
        self.importType=type
        self.editImgBtn['text'] = '编辑'+type
        self.chgPw()
        self.startRead()

    # 3.【文件】菜单
    # 3.1-7.导入图片
    def openImg(self, event=None):
        self.start(event, '图片')
        print('导入图片')

    # 3.2-8.导入文本
    def openTxt(self, event=None):
        self.start(event, '文本')
        print('打开文本')

    # 3.a-9.保存文本(封装函数)
    def saveAs(self, t1, t2=None):
        self.saveFile = asksaveasfilename(title='保存文件到', initialfile='未命名.txt', \
            filetypes=[('文本文档', '*.txt')], defaultextension='.txt')
        if not self.saveFile == '':
            with open(self.saveFile, 'w') as f:
                tmp = t1.get(1.0, END)
                if t2:
                    tmp = tmp + '\n\n' + t2.get(1.0, END)
                f.write(tmp)

    # 3.3-10.保存识别文本T1
    def saveT1(self, event=None):
        if self.pwFlag:
            self.saveAs(self.T1)
        print('保存识别文本')

    # 3.4-11.保存翻译文本T2
    def saveT2(self, event=None):
        if self.pwFlag and self.p2Flag:
            self.saveAs(self.T2)
        print('保存翻译文本')

    # 3.5-12.保存全部 合并2个文本
    def saveTxt(self, event=None):
        if self.pwFlag and self.p2Flag:
            self.saveAs(self.T1, self.T2)
        print('保存合并2个文本')

    # 3.6-13.重置/按钮和菜单
    def resetApp(self, event=None):
        print('重置')
        self.stat.set('欢迎使用！当前未打开文件')
        if self.p2Flag:
            self.T2.delete(1.0, END)
            self.chgP2()
        if self.pwFlag:
            self.T1.delete(1.0, END)
            self.chgPw()
        self.importFile = None
        self.importType = None

    # 4.【编辑】菜单
    # 4.a-14.编辑文件(封装函数)/按钮
    def editFile(self, event=None):
        if self.pwFlag:
            if self.importFile:
                os.startfile(self.importFile)
            else:
                messagebox.showinfo('信息', '未打开任何文件！')

    # 4.1-15.编辑图片
    def editImg(self, event=None):
        if self.importType == '图片':
            self.editFile()

    # 4.2-16.编辑文本
    def editTxt(self, event=None):
        if self.importType == '文本':
            self.editFile()

    # 4.3-17.格式化/按钮
    def formatTxt(self, event=None):
        txt = self.T1.get(1.0, END)
        txt = txt.replace('  ', ' ')
        txt = txt.replace('\r', '\n')
        txt = txt.replace('\n\n', '\n')
        txt = txt.replace('\n ', '')
        txt = txt.replace('', ' ')
        self.T1.delete(1.0, END)
        self.T1.insert(1.0, txt)
        txt = self.T2.get(1.0, END)
        txt = txt.replace('  ', ' ')
        txt = txt.replace('\r', '\n')
        txt = txt.replace('\n\n', '\n')
        txt = txt.replace('\n ', '')
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, txt)

    # 4.b-18.打开图片/文本目录(封装函数)
    def openFilePath(self, event=None):
        if self.pwFlag:
            (fpath, file) = os.path.split(self.importFile)
            os.startfile(fpath)
            print('打开图片/文本地址')

    # 4.4-19.打开图片目录
    def openImgPath(self, event=None):
        if self.importType == '图片':
            self.openFilePath()

    # 4.5-20.打开文本目录
    def openTxtPath(self, event=None):
        if self.importType == '文本':
            self.openFilePath()

    # 5.【工具】菜单
    # 5.1-21.切换翻译语言
    def chgLang(self, event=None):
        # print('切换语言',self.langTxt[self.lang.get()])
        self.mLangMenu['text'] = self.langTxt[self.lang.get()]

    # 5.2-22.切换翻译网站
    def chgWeb(self, event=None):
        if self.tipFlag:
            self.tipFlag = False
            messagebox.showinfo('提示', '有道翻译的"英<->日"互译不可用')
        self.mWebMenu['text'] = self.webTxt[self.web.get()]
        self.webLabel['text'] = self.webTxt[self.web.get()] + '翻译'

    # 5.3-(23-28).一键截图系列/菜单
    # a-23.初始化坐标等数据
    def createData(self):
        self.sx = 0
        self.sy = 0
        self.r = []
        self.lastDraw = 0
        self.startLine = False
        self.pastDraw = None

    # b-24.画图开始/按下事件
    def startDraw(self, event):
        self.c.delete(self.lastDraw)
        if not self.startLine:
            self.startLine = True
            self.sx = event.x
            self.sy = event.y

    # c-25.画图结束/释放事件
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

    # d-26.保存区域的图片
    def grabSave(self, type):
        self.gWin.destroy()
        self.imgTmp = grab(bbox=(self.r[0], self.r[1], self.r[2], self.r[3]))
        self.imgTmp.save('grab.jpg')
        if type == 'btn':
            self.importFile = os.getcwd() + '\\grab.jpg'
            print(self.importFile)
            self.chgState(None, '图片')

    # e-27.画矩形操作
    def myRect(self, event):
        self.startDraw(event)
        self.lastDraw = self.c.create_rectangle(self.sx, self.sy, event.x, event.y, outline='#777')

    # 5.3-28.截图入口/截图的透明窗口(蒙板)及事件(子窗口)
    def grabImg(self, type='key'):
        w = GetSystemMetrics(0)
        h = GetSystemMetrics(1)
        print('当前分辨率：', w, 'x', h)

        self.createData()
        self.gWin = Toplevel()
        self.gWin.title(' ')
        self.gWin.overrideredirect(True)
        self.gWin.attributes('-alpha', 0.4)
        self.gWin.geometry('{0}x{1}+0+0'.format(w, h))
        self.gWin.resizable(0, 0)
        self.c = Canvas(self.gWin, width=w, height=h)
        self.c.pack()
        self.gWin.bind('<KeyPress-Escape>', lambda event: self.gWin.destroy())
        self.c.bind('<B1-Motion>', self.myRect)
        self.c.bind('<ButtonRelease-1>', self.stopDraw)
        self.gWin.bind('<KeyPress-Return>', lambda event: self.grabSave(type))
        self.gWin.mainloop()

    # 5.4-(29-31).一键翻译系列/按钮
    # a-29.百度翻译
    def baiduTransMain(self, event=None):
        print('百度翻译')
        txt = self.T1.get(1.0, END)
        txt.replace('\n', '')
        ll = self.langTxt[self.lang.get()]
        (l1, l2) = ll.split('->')
        print(txt, self.baiduTrans[l1], self.baiduTrans[l2])
        url = self.transUrl[self.web.get()] + '#{0}/{1}/{2}' \
            .format(self.baiduTrans[l1], self.baiduTrans[l2], quote(txt))
        print(url)
        self.driver.get(url)
        sleep(0.6)
        self.driver.save_screenshot("trans.png")
        finds = self.driver.find_elements_by_xpath('//p[@class="ordinary-output target-output clearfix"]')
        word = ''
        for item in finds:
            word += item.text + '\n'
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, word)

    # b-30.有道翻译
    def youdaoTransMain(self, event=None):
        print('有道翻译')
        txt = self.T1.get(1.0, END)
        txt.replace('\n', '')
        self.driver.get(self.transUrl[self.web.get()])
        sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="langSelect"]/span').click()
        sleep(0.1)
        self.driver.find_element_by_xpath(
            '//*[@id="languageSelect"]/li[{0}]/a'.format(self.youdaoTrans[self.lang.get()])).click()
        sleep(0.1)
        self.driver.find_element_by_id('inputOriginal').send_keys(txt)
        sleep(0.2)
        self.driver.find_element_by_id('transMachine').click()
        finds = self.driver.find_elements_by_xpath('//*[@id="transTarget"]/p/span')
        word = ''
        for item in finds:
            word += item.text + '\n'
        sleep(0.5)
        self.driver.save_screenshot("trans.png")
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, word)

    # 5.4-31.翻译入口
    def trans(self, event=None):
        if self.pwFlag:
            if self.p2Flag == False:
                self.chgP2()
            if self.web.get() == 0:
                self.baiduTransMain()
            else:
                self.youdaoTransMain()

    # 5.5-32.切换识别语言
    def chgOcr(self, event=None):
        self.mOcrMenu['text'] = self.ocrFor[self.ocr.get()]

    # 5.6-(33-34).添加识别语言系列
    # a-33.设置语言包别名
    def aliasOk(self, filename, event=None):
        self.aliasname = self.alEntry.get()
        self.aliasname = self.aliasname.replace(' ', '')
        if self.aliasname:
            self.allOcr[filename] = self.aliasname
            with open('./MyOcr.json', 'w', encoding='utf-8') as f:
                ocrStr = dumps(self.allOcr).encode('utf-8').decode('unicode-escape')
                print(ocrStr)
                f.write(ocrStr)
            self.aliasWin.destroy()
        else:
            messagebox.showinfo('提示', '语言包的别名错误！请重新输入！')

    # 5.6-34.添加OCR入口(子窗口)
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
                messagebox.showinfo('信息', '成功添加'+filename+'语言包，重启软件生效!')
                self.aliasWin = Toplevel()
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

    # 5.7-35.打开[翻译网站](蓝色链接)
    def openTransUrl(self, event=None):
        os.startfile(self.transUrl[self.web.get()])

    # 6.[帮助]菜单
    # 6.1-36.关于(子窗口)
    def about(self, event=None):
        aboutWin = Toplevel()
        aboutWin.title('帮助和关于')
        aboutWin.geometry('500x570+500+200')
        # aboutWin.resizable(0,0)
        l = Label(aboutWin, text='Python的图片文字识别的Tkinter程序', font=('微软雅黑',16))
        l.pack(anchor='w',padx=20, pady=10)
        ttk.Separator(aboutWin).pack(fill='x', padx=5)
        with open('help.txt','r', encoding='utf-8') as f:
            ftxt = f.read()
        txt=ftxt.split('---\n')
        print(txt)
        aboutTxt = txt[0]
        helpTxt = txt[1]
        Label(aboutWin, text='关于', font=('微软雅黑',13)).pack(anchor='w',padx=40, pady=5)
        aboutLabel = Label(aboutWin, text=aboutTxt, font=('微软雅黑',11), justify='left')
        aboutLabel.pack(anchor='w',padx=50)
        Label(aboutWin, text='帮助', font=('微软雅黑', 13)).pack(anchor='w', padx=40, pady=5)
        helpLabel = Label(aboutWin, text=helpTxt, font=('微软雅黑', 11), justify='left')
        helpLabel.pack(anchor='w',padx=50)
        Label(aboutWin, text='Copyright © 2020-2021 SiWei Du. All rights reserved.', font=('黑体', 10)).pack(anchor='s', pady=20)
        aboutWin.mainloop()

    # 7.其他快捷键事件处理函数
    # 7.a-37.通过cmd获取路径(封装函数)
    def splitPath(self, cmd):
        path = os.popen(cmd).read()
        if path.find('\\')==-1:
            messagebox.showerror('错误', '未找到tessractOCR目录！请确认是否安装或配置环境变量！官方下载地址：https://sourceforge.net/projects/tesseract-ocr/')
            self.master.destroy()
        tmp = path.split('\\')
        tmp.pop()
        path = '\\'.join(tmp)
        # print(path)
        return path


    # 7.1-38.遍历文件夹，获取指定后缀文件
    def findFile(self):
        items = os.listdir(self.tessDataPath)
        newList=[]
        for item in items:
            if item.endswith('.traineddata'):
                (filename,extension)=os.path.splitext(item)
                newList.append(filename)
        print(newList)
        return newList

    # 7.2-39.文本域的字体+-(隐藏快捷键)，含义：鼠标点击事件,放大/缩小bool,改变字体的值
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