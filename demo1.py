#-*- coding:utf-8 -*-

import pytesseract as pt
from PIL import Image
import json

# import mypackage
# mypackage.fun1()

#
# obj = {'chi_sim': '中文(简)', 'chi_tra': '中文(繁)', 'eng': '英文', 'jpn': '日文', 'kor': '韩文', 'osd': 'osd?'}
# index=1
# aaa = []
# for key in obj.keys():
#     print(key)

from tkinter import *
from tkinter.font import *

tkGUI = Tk()
tkGUI.geometry('500x500+300+100')
allFonts = [item for item in families()]
allFonts = sorted(allFonts, reverse=True)

print(allFonts)

foo=Menubutton(tkGUI, text='字体1')
fv1=IntVar()
fv1.set(0)
f1 = Menu(foo)
for index, item in enumerate(allFonts):
    f1.add_radiobutton(label=item, value=index, variable=fv1, command='')

foo.config(menu=f1)
foo.pack()

tkGUI.mainloop()

# for key in obj:
#     print(key, obj[key],index)
#     index+=1


# test_dict = {'bigberg': [7600, {1: [['iPhone', 6300], ['Bike', 800], ['shirt', 300]]}]}
# print(test_dict)
# print(type(test_dict))
# #dumps 将数据转换成字符串
# json_str = json.dumps(test_dict)
# print(json_str)
# print(type(json_str))

# loads: 将 字符串 转换为 字典
# new_dict = json.loads(json_str)
# print(new_dict)
# print(type(new_dict))

# with open('./demo.json', 'w') as f:
#     json.dump(test_dict,f)

# with open('./demo.json', 'r') as f:
#     loadDict=json.load(f)
#     print(loadDict['bigberg'][1]['1'])
#     try:
#         print(loadDict['hhhhh'])
#     except KeyError:
#         print('No have')

# path = r'D:\Studysoft\OCR\tesseract.exe'
# pt.pytesseract.tesseract_cmd = path
#
# # img = Image.open('./img/en.jpg')
# img = Image.open('./img/ch.jpg')
# # img = Image.open('./img/ch2.jpg')
#
#
# # text = pt.image_to_string(img)
# text = pt.image_to_string(img, lang='chi_sim+chi_tra')
# print(text)
