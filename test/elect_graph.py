#coding=UTF-8
import wx

'''
Created on 2015??9??1??

@author: sixoloy
'''
import cv2
import Image
import ImageEnhance
import ImageFilter
import ImageDraw
import urllib
import re
import os
import pycurl
import hashlib
import string
import tempfile,sys
from threading import Thread
from pytesser import *
from numpy.lib.twodim_base import histogram2d
    

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

sys.stderr=tempfile.TemporaryFile()

#######################图像处理#############################
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
####################### 结束 #############################

hide = 1
_hide = 0
# Cookie状态
STATE = 0  
# 选课失败的报错信息
msgs = [
    '提交成功',
    '非法操作! 数据库没有对应的教学班号。',
    '当前不在此课程类别的选课时间范围内！',
    '您不在该教学班的修读对象范围内，不允许选此教学班！',
    '您所在的学生群体，在此阶段不允许对该课程类别的课进行选课、退课！',
    '系统中没有您这个学期的报到记录，不允许选课。请联系您所在院系的教务员申请补注册。',
    '您这个学期未完成评教任务，不允许选课。',
    '您不满足该教学班选课的性别要求，不能选此门课程！',
    '不允许跨校区选课！',
    '此课程已选，不能重复选择！',
    '您所选课程 的成绩为“已通过”，因此不允许再选该课，请重新选择！',
    '此类型课程已选学分总数超标',
    '此类型课程已选门数超标',
    '毕业班学生，公选学分已满，最后一个学期不允许选择公选课！',
    '您不是博雅班学生，不能选此门课程！',
    '您最多能选2门博雅班课程！',
    '您不是基础实验班学生，不能选此门课程！',
    '所选课程与已选课程上课时间冲突,请重新选择!',
    '已经超出限选人数，请选择别的课程！',
    '该教学班不参加选课，你不能选此教学班！',
    '选课等待超时',
    '您这个学期未完成缴费，不允许选课。请联系财务处帮助台（84036866 再按 3）',
    '您未满足选择该课程的先修课程条件!',
    '不在此课程类型的选课时间范围内',
    '您的核心通识课学分已满足培养方案的学分要求，无法再选择核心通识课'
            ]
courseType = {
    '专选' : 21,
    '专必' : 11,
    '公选' : 30,
    '公必' : 10,
    }
courseId = {
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
#可选课程信息块
pagePattern = re.compile(r'(?<=选课</a>)([\s\S]+?)(?=</tr>)')
#课程信息块
_pagePattern = re.compile(r'(?<=隐藏</a>)([\s\S]+?)(?=</tr>)')
#得到课程名字
coursePattern = re.compile(r'(?<=\">)(.+?)(?=</a></td>)')
#得到课程代号
courseidPattern = re.compile(r'(?<=\(\')(.+?)(?=\'\))')  
#得到课程上课时间
coursetimePattern = re.compile(u"星(.+?)）") 
#得到课程剩余人数
tdPattern = re.compile(r'(?<=\'>)(.+?)(?=</td>)')
#得到报错种类
errorPattern = re.compile(r'(?<=code\":)(.+?)(?=,\")')

##############################自定义异常########################################
class MyError(Exception):  
    def __init__(self,data=None):     #重载__init__方法  
        self.data = data  
    def __str__(self):  
        return self.data     #重载__str__方法                     
###############################图形化界面#######################################
class mainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(mainFrame, self).__init__(parent, title=title, size=(600, 400))
        self.name = None
        self.password = None
        self.jxbh = None
        self.result = None
        self.InitUI(self.name,self.name,self.name,self.name)
        self.Centre()
        self.Show()

    def InitUI(self,name,password,jxbh,result):
        panel = wx.Panel(self,-1) 
        if os.path.exists("sysu.ico"):
            self.SetIcon(wx.Icon("sysu.ico",wx.BITMAP_TYPE_ICO))
        self.vbox = wx.BoxSizer(wx.VERTICAL)   
        self.hbox = wx.BoxSizer(wx.HORIZONTAL) 
        self.str1 = wx.StaticText(panel,-1,u'学号',(1,5)) 
        self.str2 = wx.StaticText(panel,-1,u'密码',(150,5)) 
        self.str3 = wx.StaticText(panel,-1,u'课程序号',(300,5)) 
        self.str4 = wx.StaticText(panel,-1,u'课程类别',(450,5))
        self.str4 = wx.StaticText(panel,-1,u'学年度(xxxx-xxxx)',(1,70))
        self.str4 = wx.StaticText(panel,-1,u'学期',(150,70))
        self.name = wx.TextCtrl(panel,1,value="",pos=(1,30),size=(100,30))
        self.password = wx.TextCtrl(panel,1,value="",pos=(150,30),size=(100,30), style=wx.TE_PASSWORD)
        self.jxbh = wx.TextCtrl(panel,1,value=u"1",pos=(300,30),size=(100,30))
        self.xnd = wx.TextCtrl(panel,1,value=u"2015-2016",pos=(1,90),size=(100,30))
        myList_ = [u'1', u'2', u'3']
        self.xq = wx.Choice(panel,1,choices=myList_,pos=(150,90),size=(100,30))
        self.xq.SetSelection(0)
        myList = [u'公选', u'公必', u'专必', u'专选']  
        self.choice = wx.Choice(panel,1,pos=(450,30),choices=myList,size=(100,60))
        self.choice.SetSelection(3)  
        self.buttonClk = wx.Button(panel, label=u'开始抢课',pos=(1,210))
        self.buttonClk3 = wx.Button(panel, label=u'查看可选',pos=(1,180))
        self.buttonClk2 = wx.Button(panel, label=u'停止抢课',pos=(1,240))
        self.buttonClk4 = wx.Button(panel, label=u'查看全部',pos=(1,150))
        self.result = wx.TextCtrl(panel,-1,value="",pos=(100,150),size=(450,200),style=wx.TE_MULTILINE) 
        self.buttonClk.Bind(wx.EVT_BUTTON,self.OnButtonClick)
        self.buttonClk2.Bind(wx.EVT_BUTTON,self.OnButtonClick2)
        self.buttonClk3.Bind(wx.EVT_BUTTON,self.OnButtonClick3)
        self.buttonClk4.Bind(wx.EVT_BUTTON,self.OnButtonClick4)
    def OnButtonClick(self, event):
        self.user = Sysuer(self) 
        self.user.start()
    def OnButtonClick2(self, event):
        global set
        set = 0
        try:
            self.user.stop()
            self.result.AppendText( u'选课停止\r\n')  
        except:
            self.result.AppendText( u'大兄弟还没运行呢！\n')
    def OnButtonClick3(self, event):
        try:
            page = self.user.getCourse(self.xnd.Value.encode('utf-8'),self.xq.GetStringSelection().encode('utf-8'),courseType[self.choice.GetStringSelection().encode('utf-8')], self.user.sid, self.user.checkHeader_, hide )
            self.user.process(page)
        except:
            global STATE 
            STATE = 0
            self.user = Sysuer(self) 
            self.user.password = str.upper(encoding(self.user.password))
            self.user.getLoginData()
            self.user.login() 
            while STATE == 0:
                self.user.getLoginData()
                self.user.login() 
            try:
                page = self.user.getCourse(self.xnd.Value.encode('utf-8'),self.xq.GetStringSelection().encode('utf-8'),courseType[self.choice.GetStringSelection().encode('utf-8')], self.user.sid, self.user.checkHeader, hide )
                self.user.process(page)
            except:
                self.result.AppendText( u'大兄弟还没选课程类别呢！\n')
    def OnButtonClick4(self, event):
        try:
            page = self.user.getCourse(self.xnd.Value.encode('utf-8'),self.xq.GetStringSelection().encode('utf-8'),courseType[self.choice.GetStringSelection().encode('utf-8')], self.user.sid, self.user.checkHeader_, _hide )
            self.user._process(page)
        except:
            global STATE 
            STATE = 0
            self.user = Sysuer(self) 
            self.user.password = str.upper(encoding(self.user.password))
            self.user.getLoginData()
            self.user.login() 
            while STATE == 0:
                self.user.getLoginData()
                self.user.login() 
            try:
                page = self.user.getCourse(self.xnd.Value.encode('utf-8'),self.xq.GetStringSelection().encode('utf-8'),courseType[self.choice.GetStringSelection().encode('utf-8')], self.user.sid, self.user.checkHeader, hide )
                self.user.process(page)
            except:
                self.result.AppendText( u'大兄弟还没选课程类别呢！\n')
        
        
######################################   SYSU类         ##################################################
class Sysuer(Thread):
    def __init__(self, window):
        #传进来的GUI
        self.window = window
        self.cookie = None
        self.username = frame.name.Value
        self.password = frame.password.Value
        self.image = 'code' + '.jpg'
        self.rno = None
        self.code = None
        self.sid = ""
        self.url2 = None
        self.select = None
        self.urls = {
            'login': 'http://uems.sysu.edu.cn/elect/login',
            'cookie': 'http://uems.sysu.edu.cn/elect/',
            'image': 'http://uems.sysu.edu.cn/elect/login/code'
        }  
        Thread.__init__(self)
        self.stopped = False  
        self.setDaemon(True)
    #进程跑的内容
    def run(self):
        global set,FLAG,STATE
        set = 1
        FLAG = 0
        STATE = 0
        tmp = frame.jxbh.Value.encode('utf-8')
        try:
            if(len(tmp)<5):
                self.select = courseId[tmp]
            else:
                self.select = tmp  
        except:
            frame.result.AppendText( u'没有这门课！'+'\r\n')
            self.stop()
        if(self.stopped == 0):
            frame.result.AppendText( u'程序开始！'+'\r\n')
            self.password = str.upper(encoding(self.password))
            self.getLoginData()
            self.login()
            try:
                while self.stopped == 0:
                    self.Choose(self.sid,self.select)
                    while STATE!=1 :
                        self.cookie = None
                        self.getLoginData()
                        self.login()
                        self.Choose(self.sid,self.select)
            except MyError:
                self.stop()
    #结束进程
    def stop(self):
        self.stopped = True      
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
                pass
            else:
                frame.result.AppendText( u'Cookie已经过期，现在重新为你登陆!\r\n')
                STATE = 0
    #验证是否登陆成功，无STATE
    def checkHeader_(self, headerLine):
        global STATE
        result = codePattern.search(headerLine)
        if result is not None:
            if result.group() != '200':
                frame.result.AppendText( u'Cookie已经过期，现在重新为你登陆!\r\n')
                raise Exception #自己抛出一个异常
                
    def getAddress(self, data):
        global STATE
        #print data
        result = addressPattern.search(data)
        if result is not None:
            self.sid = result.group()
            STATE = 1
            frame.result.AppendText( u'登陆成功!\r\n')
                 
    def checkLogin(self, data):
        if data.find('验证码错误')!=-1 :
                self.cookie = None
                frame.result.AppendText( u'验证码错误，正在重试!\r\n')
                self.getLoginData()
                self.login() 
                pass
        elif data.find('登录失败')!=-1 :
                self.cookie = None
                frame.result.AppendText(u'密码或账户错误!\r\n') 
                raise MyError
        elif data.find('非法')!=-1 :
                self.cookie = None
                frame.result.AppendText(u'未知错误!\r\n') 
                raise MyError
    #验证是否抢课成功
    def checkError(self, data):
        error = errorPattern.search(data).group()
        if error is not None:
            str = msgs[int(error)].decode('utf-8')
            if(error != u'18'):
                frame.result.AppendText(str) 
                raise MyError
            else:
                frame.result.AppendText(str+u'\n')
                
            
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
    def getCourse(self,xnd,xq,kclb,sid,callHeader,hide = 1):
        buffer = StringIO()
        self.url = '''http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=%s&xq=%s&sid=%s&conflict=%s&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,xnd,xq,sid,hide)
        self.getData(self.url, getHeader, callHeader, buffer.write)
        return buffer.getvalue()
    def Choose(self,sid,jxbh):
        url = 'http://uems.sysu.edu.cn/elect/s/elect'
       # url2 = '''Referer:http://uems.sysu.edu.cn/elect/s/courses?kclb=%s&xqm=3&sort=&ord=&xnd=2015-2016&xq=2&sid=%s&conflict=1&blank=&hides=&fromSearch=false&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&sfbyb=''' %(kclb,sid)
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
        #chooseHeader.insert(7,url2)
        self.postData(url,chooseHeader,{
            'jxbh': jxbh,
            'sid': self.sid,
            },self.checkHeader,self.checkError)
    #处理可选课程
    def process(self,page):
        count = 1
        #print page
        result = re.findall(pagePattern,page)
        if len(result)==0 :
            frame.result.AppendText(u'\r\n没有任何课程可选!\r\n') 
        else:
            frame.result.AppendText(u'\r\n以下课程可选：\r\n') 
            for one in result:
                #得到每门课的名字
                tmp = coursePattern.search(one).group()
                tmp_ = tmp.decode('utf-8');
                string = u'%d.%s ' %(count,tmp_)
                frame.result.AppendText(string) 
                #得到每门课对应的id
                id = courseidPattern.search(one).group()
                countt = str(count)
                courseId[countt] = id
                #得到课程的信息
                one_ = one.decode('utf-8')
                inf = coursetimePattern.search(one_).group()
                frame.result.AppendText(u'%s ' %(inf)) 
                count = count+1  
                num = tdPattern.findall(one)
                num_ = num[4].decode('utf-8')
                frame.result.AppendText(u'剩余空位:%s\r\n' %(num_))
    #处理不可选课程
    def _process(self,page):
        count = 1
        #print page
        result = re.findall(_pagePattern,page)
        if len(result)==0 :
            frame.result.AppendText(u'\r\n没有任何课程可选!\r\n') 
        else:
            frame.result.AppendText(u'\r\n以下课程可选：\r\n') 
            for one in result:
                #得到每门课的名字
                tmp = coursePattern.search(one).group()
                tmp_ = tmp.decode('utf-8');
                string = u'%d.%s ' %(count,tmp_)
                frame.result.AppendText(string) 
                #得到每门课对应的id
                id = courseidPattern.search(one).group()
                countt = str(count)
                courseId[countt] = id
                #得到课程的信息
                one_ = one.decode('utf-8')
                inf = coursetimePattern.search(one_).group()
                frame.result.AppendText(u'%s ' %(inf)) 
                count = count+1  
                num = tdPattern.findall(one)
                num_ = num[4].decode('utf-8')
                frame.result.AppendText(u'剩余空位:%s\r\n' %(num_))
#md5加密
def encoding(source):
    m = hashlib.md5()
    m.update(source)
    return m.hexdigest()        


if __name__ == '__main__':
    app = wx.App()
    frame = mainFrame(None, title=u'SMIE抢课辅助V1.0                           -by Sixoloy' )
    app.MainLoop()