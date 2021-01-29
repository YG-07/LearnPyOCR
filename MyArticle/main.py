#-*- coding:utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import os

import time
from selenium import webdriver
from urllib import parse



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

    # 创建静态数据
    def createState(self):
        # 窗口大小
        self.wmin=700
        self.hmin=200
        self.hp2=550
        self.wp3=910

        # 单选标签
        self.langTxt=['','中->英','中->日','英->中','英->日','日->中','日->英']
        self.ocrTxt=['','中文(简体)','英文','日文','中文(繁)']
        self.webTxt=['','百度','有道']
        # 翻译对照
        self.baiduTrans={'中':'zh', '英':'en', '日':'jp'}

        # 字体
        self.f1='幼圆 13'
        self.f2='幼圆 12'

        # 控制面板的参数
        self.pwFlag=False
        self.p2Flag=False
        self.fxw=82*12
        self.fxw2=52*12
        self.fxh=24*12

        # 路径和网站
        # 翻译网站
        self.transUrl=['','https://fanyi.baidu.com/','http://fanyi.youdao.com/']
        # [帮助]菜单
        self.tessPath=self.splitPath('where tesseract')
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
        mFormat = Menu(menubar, tearoff=0)
        mTool = Menu(menubar, tearoff=0)
        mHelp = Menu(menubar, tearoff=0)

        # 加入主菜单
        menubar.add_cascade(label='文件(F)', menu=mFile)
        menubar.add_cascade(label='编辑(E)', menu=mEdit)
        menubar.add_cascade(label='格式(O)', menu=mFormat)
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
        mEdit.add_command(label='打开图片目录', command='')
        mEdit.add_command(label='打开文本目录', command='')

        # 3.添加[格式]的子菜单项
        mFormat.add_command(label='字体', accelerator='Ctrl+D', command='')
        mFormat.add_command(label='格式化', accelerator='Ctrl+F', command='')

        # 4.添加[工具]的子菜单项
        # 4.1二级菜单[切换翻译语言]
        self.lang = IntVar()
        self.lang.set(1)
        self.mLang = Menu(self, tearoff=0)
        self.mLang.add_radiobutton(label='中->英', value=1, variable=self.lang, command=self.chgLang)
        self.mLang.add_radiobutton(label='中->日', value=2, variable=self.lang, command=self.chgLang)
        self.mLang.add_radiobutton(label='英->中', value=3, variable=self.lang, command=self.chgLang)
        self.mLang.add_radiobutton(label='英->日', value=4, variable=self.lang, command=self.chgLang)
        self.mLang.add_radiobutton(label='日->中', value=5, variable=self.lang, command=self.chgLang)
        self.mLang.add_radiobutton(label='日->英', value=6, variable=self.lang, command=self.chgLang)
        mTool.add_cascade(label='切换翻译语言', menu=self.mLang)
        # 4.2 二级菜单[切换翻译网站]
        self.web = IntVar()
        self.web.set(1)
        mWeb = Menu(self, tearoff=0)
        mWeb.add_radiobutton(label='百度翻译', value=1, variable=self.web, command=self.chgWeb)
        mWeb.add_radiobutton(label='有道翻译', value=2, variable=self.web, command=self.chgWeb)
        mTool.add_cascade(label='切换翻译网站', menu=mWeb)
        mTool.add_command(label='一键截图', accelerator='F2', command='')
        mTool.add_command(label='一键翻译', accelerator='F3', command=self.trans)
        mTool.add_separator()

        self.ocr = IntVar()
        self.ocr.set(1)
        self.mOcr = Menu(self, tearoff=0)
        self.mOcr.add_radiobutton(label='中文(简)', value=1, variable=self.ocr, command=self.chgOcr)
        self.mOcr.add_radiobutton(label='英文', value=2, variable=self.ocr, command=self.chgOcr)
        self.mOcr.add_radiobutton(label='日文', value=3, variable=self.ocr, command=self.chgOcr)
        self.mOcr.add_radiobutton(label='中文(繁)', value=4, variable=self.ocr, command=self.chgOcr)
        mTool.add_cascade(label='切换识别语言', menu=self.mOcr)
        mTool.add_command(label='添加识别语言', command='')

        # 5.添加[帮助]的子菜单项
        mHelp.add_command(label='关于', accelerator='Ctrl+H', command=self.about)
        mHelp.add_separator()
        mHelp.add_command(label='打开OCR安装目录', command=self.openOcrPath)
        mHelp.add_command(label='下载扩展语言识别包', command=self.openOcrWeb)
        mHelp.add_separator()
        mHelp.add_command(label='tessdoc官方文档', command=self.openTessWeb)
        mHelp.add_command(label='pytesseract官方文档', command=self.openPyTessWeb)

        # 将菜单添加到主窗口
        self.master.config(menu=menubar)

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
        Label(self.top_frame, text='图片路径:', font=self.f1).pack(side='left', padx=5, pady=30)
        self.pathEntry = Entry(self.top_frame, width=40, font=('黑体', 11))
        self.pathEntry.pack(side='left', padx=2)
        self.startBtn = tk.Button(self.top_frame, width=10, text='导入并识别', font=self.f1)
        self.startBtn.pack(side='left', padx=10)
        self.grabBtn = tk.Button(self.top_frame, width=14, text='截图并识别(F2)', font=self.f1)
        self.grabBtn.pack(side='left', padx=5)

        # 面板2的[左框架]组件
        self.editImgBtn = tk.Button(self.left_frame, width=8, text='编辑图片', font=self.f2)
        self.editImgBtn.grid(row=0, column=0, sticky='nw')
        self.formatBtn = tk.Button(self.left_frame, width=6, text='格式化', font=self.f2)
        self.formatBtn.grid(row=0, column=1, sticky='nw')

        self.mOcrMenu = tk.Menubutton(self.left_frame, text='中文(简)', font=self.f2)
        self.mOcrRad = Menu(self.mOcrMenu, tearoff=0)
        self.mOcrRad.add_radiobutton(label='中文(简)', value=1, variable=self.ocr, command=self.chgOcr)
        self.mOcrRad.add_radiobutton(label='英文', value=2, variable=self.ocr, command=self.chgOcr)
        self.mOcrRad.add_radiobutton(label='日文', value=3, variable=self.ocr, command=self.chgOcr)
        self.mOcrRad.add_radiobutton(label='中文(繁)', value=4, variable=self.ocr, command=self.chgOcr)
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
        self.mLangRad.add_radiobutton(label='中->英', value=1, variable=self.lang, command=self.chgLang)
        self.mLangRad.add_radiobutton(label='中->日', value=2, variable=self.lang, command=self.chgLang)
        self.mLangRad.add_radiobutton(label='英->中', value=3, variable=self.lang, command=self.chgLang)
        self.mLangRad.add_radiobutton(label='英->日', value=4, variable=self.lang, command=self.chgLang)
        self.mLangRad.add_radiobutton(label='日->中', value=5, variable=self.lang, command=self.chgLang)
        self.mLangRad.add_radiobutton(label='日->英', value=6, variable=self.lang, command=self.chgLang)
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
        self.startBtn.bind('<Button-1>', self.start)
        self.grabBtn.bind('<Button-1>', self.grabStart)
        self.showBtn.bind('<Button-1>', self.chgP2)

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
        self.master.bind('<KeyPress-F2>', lambda event: self.grabImg(event))
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

    # 事件和函数
    # 分割主面板pw
    def chgPw(self, event=None):
        if not self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hp2))
            self.master.minsize(self.wmin, self.hp2)
            self.startBtn['text'] = '重置'
            self.grabBtn.pack_forget()
            self.pw['height'] = 450
            self.pw.add(self.p2)
            self.p2.add(self.left_frame)
        elif self.pwFlag:
            self.master.geometry('{0}x{1}'.format(self.wmin,self.hmin))
            self.master.minsize(self.wmin, self.hmin)
            self.startBtn['text'] = '导入并识别'
            self.grabBtn.pack(side='left', padx=5)
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
        self.chgPw()
        self.T1.insert(1.0, '大家好')

    # 2.[截图并识别]按钮的事件
    def grabStart(self, event):
        self.chgPw()

    # 快捷键和菜单事件处理函数
    # 1.[文件]菜单
    # 1.导入图片
    def openImg(self, event=None):
        print('导入图片')

    # 2.打开文本
    def openTxt(self, event=None):
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
        print('格式化')

    # 4.[工具]菜单
    # 1.切换识别语言
    def chgOcr(self, event=None):
        self.mOcrMenu['text'] = self.ocrTxt[self.ocr.get()]

    # 2.添加识别语言
    def addOcr(self, event):
        print('添加识别语言')
        # askopenfilename

    # 3.一键截图
    def grabImg(self, event=None):
        if (self.pwFlag==False) and (self.p2Flag==False):
            print('一键截图')

    # 4.一键翻译
    def transMain(self, event=None):
        print('一键翻译')
        txt = self.T1.get(1.0, END)
        txt.replace('\n', '')
        ll = self.langTxt[self.lang.get()]
        (l1, l2) = ll.split('->')
        print(txt, self.baiduTrans[l1], self.baiduTrans[l2])
        url = self.transUrl[self.web.get()] + '#{0}/{1}/{2}'.format(self.baiduTrans[l1], self.baiduTrans[l2],
                                                                    parse.quote(txt))
        print(url)
        self.driver.get(url)
        time.sleep(1)
        self.driver.save_screenshot("trans.png")
        finds = self.driver.find_elements_by_xpath('//*[@class="output-bd"]/p/span')
        word = ''
        for item in finds:
            word += item.text + '\n'
        self.T2.delete(1.0, END)
        self.T2.insert(1.0, word)

    def trans(self, event=None):
        if self.pwFlag:
            if self.p2Flag == False:
                self.chgP2()
            self.transMain()


    # 5.切换语言
    def chgLang(self, event=None):
        # print('切换语言',self.langTxt[self.lang.get()])
        self.mLangMenu['text']=self.langTxt[self.lang.get()]


    # 6.切换网站
    def chgWeb(self, event=None):
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
        print('打开OCR目录')
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