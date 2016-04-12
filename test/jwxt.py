#encoding=UTF-8
'''
Created on 2015??9??1??

@author: sixoloy
'''
import urllib
import re
import json
import uuid
import os
import pycurl
import hashlib
import string
from verification import *

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

loginHeader = [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'Cache-Control: max-age=0',
    'Connection: keep-alive',
    'Host: uems.sysu.edu.cn',
    'Origin: http://uems.sysu.edu.cn',
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
    'Content-Type: application/x-www-form-urlencoded',
    ]

getHeader = [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'Connection: keep-alive',
    'Host: uems.sysu.edu.cn',
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
]

postHeader = [
    'Accept: */*',
    'ajaxRequest: true',
    'render: unieap',
    'Content-Type: multipart/form-data',
    'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; InfoPath.3; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; Shuame)',
    'Host: uems.sysu.edu.cn',
    'Connection: Keep-Alive',
    'Cache-Control: no-cache',
]

cookiePattern = re.compile(r'(?<=Set-Cookie:\ )(.+?)(?=;)')
codePattern = re.compile(r'(?<=HTTP/1.1\ )(.+?)(?=\ )')
rnoPattern = re.compile(r'(?<=rno\"\ value=)(.+?)(?=\>)')
scorePattern1 = re.compile(r'(?<=kcmc\":\")(.+?)(?=\",)')
scorePattern2 = re.compile(r'(?<=xf\":\")(.+?)(?=\",)')
scorePattern3 = re.compile(r'(?<=zzcj\":\")(.+?)(?=\",)')
scorePattern4 = re.compile(r'(?<=jxbpm\":\")(.+?)(?=\",)')

class Sysuer:
    def __init__(self, *args, **kwargs):
        self.cookie = None
        self.username = '13354446'
        self.password = '0502303X'
        self.image = 'code' + '.jpg'
        self.rno = None
        self.code = None
        self.urls = {
            'login': 'http://uems.sysu.edu.cn/jwxt/j_unieap_security_check.do',
            'cookie': 'http://uems.sysu.edu.cn/jwxt/',
            'image': 'http://uems.sysu.edu.cn/jwxt/jcaptcha',
            'student': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=judgeStu',
            'score': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getKccjList',
            'grade': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getAllJd',
            'credit': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getAllXf',
            'totalCredit': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getZyxf',
            'lesson': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getCjlcList',
            'detail': 'http://uems.sysu.edu.cn/jwxt/xscjcxAction/xscjcxAction.action?method=getFxcj',
            'school': 'http://uems.sysu.edu.cn/jwxt/quanxianLd/qxldAction.action?method=getYxxxList',
            'department': 'http://uems.sysu.edu.cn/jwxt/quanxianLd/qxldAction.action?method=getAllXsxxList',
            'profession': 'http://uems.sysu.edu.cn/jwxt/quanxianLd/qxldAction.action?method=getAllZyxxList',
            'direction': 'http://uems.sysu.edu.cn/jwxt/quanxianLd/qxldAction.action?method=getNdzyfxmcByzyfxmView',
            'courses': 'http://uems.sysu.edu.cn/jwxt/ZxxkmdtzModule/ZxxkmdtzAction.action?method=getAllJxbxx',
            'selection': 'http://uems.sysu.edu.cn/jwxt/xstk/xstk.action?method=getXsxkjgxxlistByxh',
            'table': 'http://uems.sysu.edu.cn/jwxt/KcbcxAction/KcbcxAction.action?method=getList',
        }
    #接收数据    
    def getData(self, url, headerCallback, callback):
        connect = pycurl.Curl()
        connect.setopt(connect.URL, url)
        connect.setopt(connect.HTTPHEADER, getHeader)
        connect.setopt(connect.HEADERFUNCTION, headerCallback)
        connect.setopt(connect.WRITEFUNCTION, callback)
        connect.setopt(connect.COOKIE, self.cookie)
        connect.perform()
        connect.close()
    #发送数据    
    def postData(self, url, header, data, headerCallback, callback):
        try:
            data = urllib.urlencode(data)
        except:
            pass
        connect = pycurl.Curl()
        connect.setopt(connect.URL, url)
        connect.setopt(connect.HTTPHEADER, header)
        #connect.setopt(connect.FOLLOWLOCATION, True)
        connect.setopt(connect.POST, True)
        connect.setopt(connect.POSTFIELDS, data)
        connect.setopt(connect.COOKIE, self.cookie)
        connect.setopt(connect.HEADERFUNCTION, headerCallback)
        connect.setopt(connect.WRITEFUNCTION, callback)
        connect.perform()
        connect.close()    
            
    def getLoginData(self):
        self.getCookie()
        self.getImage()
        self.getRno() 
        name = 'media/code.jpg'
        self.code = getverify1(name)
        
    def getCookie(self):
        self.getData(self.urls['cookie'],self.cookieHeaderFunction, self.passWrite)

    def getImage(self):
        path = 'media/' + self.image
        code = open(path, 'wb')
        connect = pycurl.Curl()
        connect.setopt(connect.URL, self.urls['image'])
        connect.setopt(connect.HTTPHEADER, getHeader)
        connect.setopt(connect.WRITEDATA, code)
        connect.setopt(connect.COOKIE, self.cookie)
        connect.perform()
        connect.close()
        code.close()

    def getRno(self):
        self.getData(self.urls['cookie'],self.passHeader, self.rnoWrite)
        
    def passHeader(self, headerLine):
        pass

    def passWrite(self, data):
        pass

    def rnoWrite(self, data):
        result = rnoPattern.search(data)
        if result:
            self.rno = result.group()
    def cookieHeaderFunction(self, headerLine):
        field = headerLine.split(':')[0]
        if field == 'Set-Cookie':
            cookie = cookiePattern.search(headerLine).group()
            self.cookie = cookie 
    #验证是否登陆成功
    def loginHeader(self, headerLine):
        result = codePattern.search(headerLine)
        if result is not None:
            if result.group() != '302':
                self.cookie = None
                raise Exception('The username or password is not correct')        
    #获取了一切信息之后开始登陆        
    def login(self):
        if self.cookie is None:
            raise Exception('The cookie is emtpy')
#         buffer = StringIO.StringIO()
        self.postData(self.urls['login'], loginHeader, {
            'j_username': self.username,
            'j_password': self.password,
            'rno': self.rno,
            'jcaptcha_response': self.code,
            }, self.loginHeader, self.passWrite)    
        #print buffer.getvalue()   
    #获取成绩
    def getScore(self, year='', term='', type='', yearCondition='=', termCondition='=', typeCondition='='):
        if self.cookie is None:
            self.login()
        if year == '':
            year = 'none'
            yearCondition = '!='
        if term == '':
            term = 'none'
            termCondition = '!='
        if type == '':
            type = 'none'
            typeCondition = '!='
        buffer = StringIO()
        data = '''{header:{"code": -100, "message": {"title": "", "detail": ""}},body:{dataStores:{kccjStore:{rowSet:{"primary":[],"filter":[],"delete":[]},name:"kccjStore",pageNumber:1,pageSize:100,recordCount:0,rowSetName:"pojo_com.neusoft.education.sysu.xscj.xscjcx.model.KccjModel",order:"t.xn, t.xq, t.kch, t.bzw"}},parameters:{"kccjStore-params": [{"name": "Filter_t.pylbm_0.6220199986403405", "type": "String", "value": "'%s'", "condition": " %s ", "property": "t.pylbm"}, {"name": "Filter_t.xn_0.17289099200582425", "type": "String", "value": "'%s'", "condition": " %s ", "property": "t.xn"}, {"name": "Filter_t.xq", "type": "String", "value": "'%s'", "condition": " %s ", "property": "t.xq"}], "args": ["student"]}}}''' % (type, typeCondition, year, yearCondition, term, termCondition)
        self.postData(self.urls['score'], postHeader, data, self.passHeader, buffer.write)
        return buffer.getvalue()
        
#md5加密
def encoding(source):
    m = hashlib.md5()
    m.update(source)
    return m.hexdigest()
#计算绩点
def calGPA(credits,marks):
    sum = 0
    tmp = 0
    for i in xrange(len(credits)):
        credits[i] = float(credits[i])
        marks[i] = float(marks[i])/10-5
        sum += credits[i]*marks[i]
        tmp += credits[i]
    return sum/tmp
    
#主框架
if __name__ == '__main__':
    #md5加密
    user = Sysuer()
#     user.username = raw_input('学号:')
#     user.password = raw_input('密码:')
    user.password = str.upper(encoding(user.password))
    user.getLoginData()
    user.login()
    page = user.getScore('2014-2015','3','01')
    name1 = scorePattern1.findall(page)#课程名字
    name2 = scorePattern2.findall(page)#学分
    name3 = scorePattern3.findall(page)#成绩
    name4 = scorePattern4.findall(page)#排名
    for i in range(len(name1)):
        name4[i] = name4[i].replace('\\','')
        print name1[i],' 学分',name2[i],' 成绩',name3[i],' 排名',name4[i]
    print '你本学期绩点为：%.3f' %calGPA(name2, name3)
                   