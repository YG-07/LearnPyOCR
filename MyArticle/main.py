#-*- coding:utf-8 -*-

from tkinter import *
from tkinter import messagebox

class Application(Frame):
    # 一个经典的GUI程序
    def __init__(self, master=None):
        #super()是父类的构造器
        super().__init__(master)
        self.master = master
        self.pack()

        self.createState()
        self.createWidget()

    # 创建静态数据
    def createState(self):
        pass

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
        mFile.add_command(label='导入图片', accelerator='Ctrl+N', command='')
        mFile.add_command(label='导入文本', accelerator='Ctrl+O', command='')
        mFile.add_separator()
        mFile.add_command(label='保存识别文本', accelerator='Ctrl+1', command='')
        mFile.add_command(label='保存翻译文本', accelerator='Ctrl+2', command='')
        mFile.add_command(label='保存全部', accelerator='Ctrl+S', command='')
        mFile.add_separator()
        mFile.add_command(label='重置', accelerator='Ctrl+R', command='')
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
        mLang = Menu(self, tearoff=0)
        mLang.add_radiobutton(label='中->英', value=1, variable=self.lang, command='')
        mLang.add_radiobutton(label='中->日', value=2, variable=self.lang, command='')
        mLang.add_radiobutton(label='英->中', value=3, variable=self.lang, command='')
        mLang.add_radiobutton(label='英->日', value=4, variable=self.lang, command='')
        mLang.add_radiobutton(label='日->中', value=5, variable=self.lang, command='')
        mLang.add_radiobutton(label='日->英', value=6, variable=self.lang, command='')
        mTool.add_cascade(label='切换翻译语言', menu=mLang)
        # 4.2 二级菜单[切换翻译网站]
        self.web = IntVar()
        self.web.set(1)
        mWeb = Menu(self, tearoff=0)
        mWeb.add_radiobutton(label='百度翻译', value=1, variable=self.web, command='')
        mWeb.add_radiobutton(label='有道翻译', value=2, variable=self.web, command='')
        mTool.add_cascade(label='切换翻译网站', menu=mWeb)
        mTool.add_command(label='一键截图', accelerator='F2', command='')
        mTool.add_command(label='一键翻译', accelerator='F3', command='')
        mTool.add_separator()
        mTool.add_command(label='切换识别语言', command='')
        mTool.add_command(label='添加识别语言', command='')

        # 5.添加[帮助]的子菜单项
        mHelp.add_command(label='关于', accelerator='Ctrl+H', command='')
        mHelp.add_separator()
        mHelp.add_command(label='打开OCR安装目录', command='')
        mHelp.add_command(label='下载扩展语言识别包', command='')
        mHelp.add_separator()
        mHelp.add_command(label='tessdoc官方文档', command='')
        mHelp.add_command(label='pytesseract文档', command='')

        # 将菜单添加到主窗口
        self.master.config(menu=menubar)


if __name__ == '__main__':
    root = Tk()
    root.title('图片文字识别程序')
    root.geometry('650x550+200+160')
    app = Application(master=root)
    root.mainloop()