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
import time
from verification2 import *

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

zhuanxuan = 21
zhuanbi = 11
gongxuan = 30
gongbi = 10
hide = 1
_hide = 0
# 是否抢到课
FLAG = 0
# Cookie状态
STATE = 0  
courseId = {
    '移动应用开发': '46000103152006',
    '物联网技术导论': '46000105152002',  
    '人工智能':'46000088152002'
    }
loginHeader = [
    'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding:gzip, deflate',
    'Accept-Language:zh-CN,zh;q=0.8',
    'Cache-Control:max-age=0',
    'Connection:keep-alive',
    'Content-Type:application/x-www-form-urlencoded',
    'Host:uems.sysu.edu.cn',
    'Origin:http://uems.sysu.edu.cn',
    'Referer:http://uems.sysu.edu.cn/elect/',
    'Upgrade-Insecure-Requests:1',
    'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    ]

getHeader = [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
    'Connection: keep-alive',
    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36',
]

postHeader = [
    'Host: uems.sysu.edu.cn',
    'Connection: keep-alive',
    'Accept: */*',
    'Origin: http://uems.sysu.edu.cn',
    'X-Requested-With: XMLHttpRequest',
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding: gzip, deflate',
    'Accept-Language: zh-CN,zh;q=0.8'
]

cookiePattern = re.compile(r'(?<=Set-Cookie:\ )(.+?)(?=;)')
codePattern = re.compile(r'(?<=HTTP/1.1\ )(.+?)(?=\ )')
rnoPattern = re.compile(r'(?<=rno\"\ value=)(.+?)(?=\>)')
scorePattern1 = re.compile(r'(?<=kcmc\":\")(.+?)(?=\",)')
scorePattern2 = re.compile(r'(?<=xf\":\")(.+?)(?=\",)')
scorePattern3 = re.compile(r'(?<=zzcj\":\")(.+?)(?=\",)')
scorePattern4 = re.compile(r'(?<=jxbpm\":\")(.+?)(?=\",)')
addressPattern = re.compile(r'(?<=sid=)(.+?)(?=\s)')

class Sysuer:
    def __init__(self, *args, **kwargs):
        self.cookie = None
        self.username = '13354446'
        self.password = '0502303X'
        self.image = 'code' + '.jpg'
        self.rno = None
        self.code = None
        self.sid = ""
        self.url2 = None
        self.select = courseId['物联网技术导论']
        self.urls = {
            'login': 'http://uems.sysu.edu.cn/elect/login',
            'cookie': 'http://uems.sysu.edu.cn/elect/',
            'image': 'http://uems.sysu.edu.cn/elect/login/code'
        }
    #接收数据    
    def getData(self, url, header, headerCallback, callback):
        connect = pycurl.Curl()
        connect.setopt(connect.URL, url)
        connect.setopt(connect.HTTPHEADER, header)
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
        #connect.setopt(connect.CURLOPT_USERAGENT,"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/8.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3)")
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
        name = 'media/code.jpg'
        self.code = getverify1(name)
        
    def getCookie(self):
        self.getData(self.urls['cookie'], getHeader, self.cookieHeaderFunction, self.passWrite)

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
        
    #验证是否登陆有效
    def loginHeader(self, headerLine):
        result = codePattern.search(headerLine)
        if result is not None:
            if result.group() != '302':
                self.cookie = None
                raise Exception('The username or password is not correct')    
        
    def passHeader(self, headerLine):
        pass
    
    def passWrite(self, data):
        pass
    
    #验证是否登陆成功
    def checkHeader(self, headerLine):
        global STATE
        result = codePattern.search(headerLine)
        if result is not None:
            if result.group() == '200':
                STATE = 1
                print 'Cookie正常，正在查看是否有课!'
            else:
                print 'Cookie已经过期，现在重新为你登陆!'
                STATE = 0
                
    #验证是否抢课成功
    def checkData(self, data):
        global FLAG
        page = data
        pattern = '''courseDet(\'%s\', \'2015-2016\', \'2\'''' %(self.select)
        result = page.find(pattern)
        if result!= -1:
            FLAG = FLAG+1
        else:
            pass
            
              
    def loginHeader(self, headerLine):
        print headerLine
        result = codePattern.search(headerLine)
        if result is not None:
            if result.group() != '302':
                self.cookie = None
                raise Exception('The username or password is not correct')   
    def getAddress(self, data):
        global STATE
        #print data
        result = addressPattern.search(data)
        if result is not None:
            self.sid = result.group()
            STATE = 1
            print '登陆成功!'
                 
    def checkLogin(self, data):
        if data.find('验证码错误')!=-1 :
                self.cookie = None
                print '验证码错误，正在重试!'
                self.getLoginData()
                self.login() 
                pass
        elif data.find('登录失败')!=-1 :
                self.cookie = None
                raise Exception('密码或账户错误!') 
        elif data.find('非法')!=-1 :
                self.cookie = None
                raise Exception('未知错误!') 

    def cookieHeaderFunction(self, headerLine):
        field = headerLine.split(':')[0]
        if field == 'Set-Cookie':
            cookie = cookiePattern.search(headerLine).group()
            self.cookie = cookie  
    def login(self):
        if self.cookie is None:
            raise Exception('The cookie is emtpy')
        self.postData(self.urls['login'], loginHeader, {
        'username':self.username,
        'password':self.password,
        'j_code':self.code,
        'lt':None,
        '_eventId':'submit',
        'gateway':'true',
        }, self.getAddress, self.checkLogin)    
     #获取可选课程
    def getCourse(self,kclb,sid,hide = 1):
        self.url = '''http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=2015-2016&xq=2&sid=%s&conflict=%s&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,sid,hide)
        self.getData(self.url, getHeader, self.passHeader, self.passWrite)
    #验证是否抢课成功  
    def getVerify(self,kclb,sid,hide = 0):
        url = '''http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=2015-2016&xq=2&sid=%s&conflict=%s&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,sid,hide)
        url2 = '''Referer:http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=2015-2016&xq=2&sid=%s&conflict=&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,sid)
        VerifyHeader = [
            'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding:gzip, deflate, sdch',
            'Accept-Language:zh-CN,zh;q=0.8',
            'Connection:keep-alive',
            'Host:uems.sysu.edu.cn',
            'Upgrade-Insecure-Requests:1',
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        ]
        VerifyHeader.insert(5,url2)
        self.getData(url, VerifyHeader, self.passHeader, self.checkData)
    def Choose(self,sid,jxbh,kclb):
        url = 'http://uems.sysu.edu.cn/elect/s/elect'
        url2 = '''Referer:http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=2015-2016&xq=2&sid=%s&conflict=1&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,sid)
        chooseHeader = [
            'Accept:*/*',
            'Accept-Encoding:gzip, deflate',
            'Accept-Language:zh-CN,zh;q=0.8',
            'Connection:keep-alive',
            'Content-Type:application/x-www-form-urlencoded; charset=UTF-8',
            'Host:uems.sysu.edu.cn',
            'Origin:http://uems.sysu.edu.cn',
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
            'X-Requested-With:XMLHttpRequest',
        ]
        chooseHeader.insert(7,url2)
        self.postData(url,chooseHeader,{
            'jxbh': jxbh,
            'sid': self.sid,
            },self.checkHeader,self.passWrite)
#md5加密
def encoding(source):
    m = hashlib.md5()
    m.update(source)
    return m.hexdigest()
    
#主框架
if __name__ == '__main__':
    user = Sysuer()
    #     user.username = raw_input('学号:')
    #     user.password = raw_input('密码:')
    name = raw_input('请输入你想选择的课程名字：')
    print '开始程序！'
    user.select = courseId[name]
    user.password = str.upper(encoding(user.password))
    user.getLoginData()
    user.login()
    while FLAG == 0:
        user.Choose(user.sid,user.select,zhuanxuan)
        while STATE!=1 :
            user.cookie = None
            user.getLoginData()
            user.login()
            user.Choose(user.sid,user.select,zhuanxuan)
        user.getVerify(zhuanxuan,user.sid,_hide)
    print '选课成功'
                   