#encoding=UTF-8
'''
Created on 2015��8��31��

@author: sixoloy
'''
import cv2
import Image
import ImageEnhance
import ImageFilter
import ImageDraw
from pytesser import *
from numpy.lib.twodim_base import histogram2d

# 二值化
threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

#转换
rep={'/':'J',
     ' ':'',
     ':':'J',
     '0':'O',
     '!':'I'
    };
def  getverify1(name):
    
    #打开图片
    im = Image.open(name)
    #�õ�ͼƬ�Ŀ��
    h,w = im.size
    #转化到亮度
    im = im.filter(ImageFilter.MedianFilter())
    imgry = im.convert('L')
    pix = imgry.load()
    #画直方图
    count = [0]*256
    for i in xrange(h):
        for j in xrange(w):
            value = pix[i,j]
            count[value]+=1;
    img = Image.new('RGB',(256,256),(256,256,256))        
    draw = ImageDraw.Draw(img)     
    s = max(count)
    for k in xrange(256):
        #归一化
        count[k] = count[k]*200/s
        source = (k,255)
        target = (k,255-count[k])
        draw.line([source,target],(100,100,100))   
    #二值化
    out = imgry.point(table,'1')
    #剪裁区域
    box = (2,2,65,18)
    out = out.crop(box)
    #out.show()
    #识别
    text = image_to_string(out)
    #识别对吗
    text = text.strip()
    text = text.upper();
    for r in rep:
        text = text.replace(r,rep[r])

    #out.save(text+'.jpg')
    return text
