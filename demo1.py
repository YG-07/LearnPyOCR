#-*- coding:utf-8 -*-

import pytesseract as pt
from PIL import Image

path = r'D:\Studysoft\OCR\tesseract.exe'
pt.pytesseract.tesseract_cmd = path

# img = Image.open('./img/en.jpg')
img = Image.open('./img/ch.jpg')
# img = Image.open('./img/ch2.jpg')


# text = pt.image_to_string(img)
text = pt.image_to_string(img, lang='chi_sim+chi_tra')
print(text)
