# -*- coding:utf-8 -*-
import wx
import pymysql
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import constants
from lxml import etree
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from cardcode import CardCode
import time
from PIL import Image
import json
# import logging
# from logging.handlers import RotatingFileHandler

flag = False

# log_file = 'log.log'
# root_logging = logging.getLogger()
# root_logging.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s [%(name)s:%(filename)s:%(lineno)d] [%(levelname)s]- %(message)s')
# # 文件最大2M
# rotating_file_log = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=3)
# rotating_file_log.setLevel(logging.INFO)
# rotating_file_log.setFormatter(formatter)
# root_logging.addHandler(rotating_file_log)

success_user_list = ''
failed_user_list = ''

def connect_db():
    db = pymysql.connect(host='cd-cdb-nmj4h99o.sql.tencentcdb.com', user='bryant', password='leekobe24', db='blog',
                         port=63625, charset='utf8')
    print('连接数据库成功！')
    return db

def open_start_thread(success_info, failed_info, member_id, use_times, status=1):
    executor = ThreadPoolExecutor(max_workers=int(use_times))
    print(status)
    # # user_id = get_uuid(32)
    # # mac_site = get_mac_address()
    # print('开启线程')
    # while True:
    db = connect_db()
    conn = db.cursor()  # 获取指针以操作数据库
    if status == 1:
        sql = 'SELECT user, password, name  FROM blog WHERE status=0 and member_id=%d ORDER BY id' % member_id
    else:
        sql = 'SELECT user, password, name  FROM blog WHERE status=-1 and member_id=%d ORDER BY id' % member_id
    conn.execute(sql)
    blog_list = conn.fetchall()
    for image_name, item in enumerate(blog_list):
        task = executor.submit(start, success_info, failed_info, item, image_name)
        if flag:
            print('关闭线程')
            task.cancel()
            return
        time.sleep(3)


def start(success_info, failed_info, item, image_name):
    db = connect_db()
    conn = db.cursor()  # 获取指针以操作数据库
    # sql = 'SELECT user, password, name  FROM blog WHERE status=0 and member_id=%d ORDER BY id' % member_id
    # conn.execute(sql)
    # blog_list = conn.fetchall()
    print('开始运行')
    # print(blog_list)
    # for item in blog_list:
    print(item)
    user = item[0]
    password = item[1]
    name = item[2]
    sql = "UPDATE blog SET status = -1 WHERE user = %s" % user
    print('修改数据为-1')
    conn.execute(sql)
    db.commit()
    print(user, password, name, image_name)
    check = sendmessage(user, password, image_name)
    if check:
        print('成功')
        sql = "UPDATE blog SET status = 1 WHERE user = %s" % user
        conn.execute(sql)
        db.commit()
        global success_user_list
        info = user + '----' + password + '----' + name
        success_user_list += info + '\n'
    else:
        print('失败')
        global failed_user_list
        info = user + '----' + password + '----' + name
        failed_user_list += info + '\n'
        print(failed_user_list)
    success_info.SetValue(success_user_list)
    failed_info.SetValue(failed_user_list)


def getphone():

    while True:
        phone_url = 'http://huoyun888.cn/api/do.php?action=getPhone&token=903e64acc9b2a43985353bc2e0809c9c&sid=11818&phoneType=CMCC'
        response = requests.get(phone_url).text
        if '余额不足' in response:
            url = 'http://huoyun888.cn/api/do.php?action=cancelAllRecv&token=903e64acc9b2a43985353bc2e0809c9c&sid=11818phoneType=CMCC'
            requests.get(url)
        else:
            phone = response.split('|')[1]
            return phone


def putSentMessage(phone, message_content, addressee):
    author = 'daidaicu'
    putSentMessage = 'http://huoyun888.cn/api/do.php?action=putSentMessage&phone=' + phone + '&sid=' + '11818' + '&message=' + message_content + '&recvPhone=' + addressee + '&token=903e64acc9b2a43985353bc2e0809c9c' + '&author=' + author
    while True:
        response = requests.get(putSentMessage).text
        time.sleep(3)
        if '1' in response:
            print(response)
            return phone
        if '提交失败' in response:
            return -1


def getSentMessageStatus(phone):
    flag = True
    getSentMessageStatus = 'http://huoyun888.cn/api/do.php?action=getSentMessageStatus&phone=' + phone + '&sid=' + '11818' + '&token=903e64acc9b2a43985353bc2e0809c9c'
    while True:
        response = requests.get(getSentMessageStatus).text
        time.sleep(3)
        print(response)
        if '1' in response:
            flag = False
            print('发送成功')
            return flag
        if '发送失败' in response:
            return flag
        if '手机号不在线或手机号已释放，可尝试检查发码是否成功。' in response:
            return flag

def get_ip():
    url = 'http://dps.kdlapi.com/api/getdps/?orderid=994885572240867&num=1&pt=1&ut=2&format=json&sep=1'
    ip_list = json.loads(requests.get(url).text).get('data').get('proxy_list')
    ip = random.choice(ip_list)
    return ip

def get_browser(user):
    while True:
        print('获取ip')
        url = 'https://login.sina.com.cn/signup/signin.php'

        chrome_options = Options()
        # 在Linux需要禁用sandbox
        chrome_options.add_argument('--no-sandbox')
        # 谷歌文档提到需要加上这个属性来规避bug
        # chrome_options.add_argument('--disable-gpu')
        # 隐藏滚动条, 应对一些特殊页面
        # chrome_options.add_argument('--hide-scrollbars')
        # 不加载图片, 提升速度
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # https安全问题
        chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # 添加代理
        ip = get_ip()
        chrome_options.add_argument("--proxy-server=http://" + ip)
        # 随机user_agent
        user_agent = random.choice(constants.USER_AGENTS)
        chrome_options.add_argument('user-agent=%s' % user_agent)
        # logging.info("opening chrome, catalog_url:%s", catalog_url)

        browser = webdriver.Chrome(chrome_options=chrome_options)
        try:
            browser.get(url)
            browser.set_page_load_timeout(5)
            time.sleep(2)
            browser.find_element("name", "username").send_keys(user)
            browser.quit()
            return ip
        except:
            browser.quit()
            continue

def new_screen(browser, captcha_url, image_name):
    print('获取验证码截图')
    js = 'window.open("' + captcha_url[0] + '");'
    browser.execute_script(js)

    blog_screen = browser.current_window_handle

    handles = browser.window_handles

    check_screen = None
    for handle in handles:
        if handle != blog_screen:
            check_screen = handle
    # 输出当前窗口句柄（搜狗）
    browser.switch_to.window(check_screen)
    check_image =str(image_name) + '.png'
    browser.get_screenshot_as_file(check_image)
    img = Image.open(check_image)
    img = img.crop([img.size[0]/4,img.size[1]/4,img.size[0]*3/4,img.size[1]*3/4])
    img.save(check_image)
    browser.close()  # 关闭当前窗口（搜狗）
    # 切换回百度窗口
    browser.switch_to.window(blog_screen)
    print('获取验证码截图成功')
    return bytes(check_image, encoding="utf8")

def sendmessage(user, password, image_name):
    while True:
        ip = get_browser(user)
        print('进入程序')
        print('当前ip可用')
        url = 'https://login.sina.com.cn/signup/signin.php'

        chrome_options = Options()
        # 在Linux需要禁用sandbox
        chrome_options.add_argument('--no-sandbox')
        # 谷歌文档提到需要加上这个属性来规避bug
        # chrome_options.add_argument('--disable-gpu')
        # 隐藏滚动条, 应对一些特殊页面
        # chrome_options.add_argument('--hide-scrollbars')
        # 不加载图片, 提升速度
        # chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # https安全问题
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless')
        # 添加代理
        # ip = get_ip()
        chrome_options.add_argument("--proxy-server=http://" + ip)
        # 随机user_agent
        user_agent = random.choice(constants.USER_AGENTS)
        chrome_options.add_argument('user-agent=%s' % user_agent)
        # logging.info("opening chrome, catalog_url:%s", catalog_url)

        browser = webdriver.Chrome(chrome_options=chrome_options)
        # browser.set_page_load_timeout(60)
        browser.get(url)
        # browser.implicitly_wait(3)
        try:
            browser.find_element("name", "username").send_keys(user)
            break
        except:
            browser.quit()
            continue

    browser.find_element("name", "password").send_keys(password)
    time.sleep(3)
    browser.find_elements_by_xpath("//input[@class='W_btn_a btn_34px']")[0].click()
    time.sleep(3)

    html = browser.page_source
    sel = etree.HTML(html)
    while True:
        cardcode = CardCode()
        if browser.current_url != url:
            break
        captcha_url = sel.xpath("//img[@id='check_img']/@src")
        b_image_name = new_screen(browser, captcha_url, image_name)
        result = cardcode.__vaild__(b_image_name)
        # result = input('验证码：')
        browser.find_elements_by_xpath("//input[@id='door']")[0].clear()
        browser.find_element("name", "door").send_keys(bytes.decode(result, 'gbk'))
        # browser.find_element("name", "door").send_keys(result)
        browser.find_elements_by_xpath("//input[@class='W_btn_a btn_34px']")[0].click()
        time.sleep(2)
        current_url = browser.current_url
        if current_url == 'http://my.sina.com.cn/':
            break
        if current_url == 'http://i.blog.sina.com.cn/':
            return True
        html = browser.page_source
        sel = etree.HTML(html)
        check_result = sel.xpath("//span[@class='form_prompt']/i/text()")[0]
        if check_result != '输入的验证码不正确':
            break

    browser.find_elements_by_xpath("//li[@class='l_pdt l_pdt1']/a/span")[0].click()
    time.sleep(2)
    # 获取打开的多个窗口句柄
    windows = browser.window_handles
    # 切换到当前最新打开的窗口
    browser.switch_to.window(windows[-1])
    # url = 'http://control.blog.sina.com.cn/myblog/htmlsource/blog_notopen.php?uid=' + name + '&version=7'
    if browser.current_url == 'http://i.blog.sina.com.cn/':
        cookies = browser.get_cookies()
        for item in cookies:
            if item.get('name') == 'SUB':
                result = user + '----' + password + '----\n' + item.get('value') + '\n'
                with open('cookies.txt', 'a') as f:
                    f.write(result)
                break
        # print('cookies：', cookies)
        time.sleep(2)
        browser.quit()
        return True

    # browser.refresh()
    try:
        html = browser.page_source
        sel = etree.HTML(html)
        check_user = sel.xpath("//p[@class ='notOpen_title']/strong/text()")[0]
        if '很抱歉' in check_user:
            cookies = browser.get_cookies()
            for item in cookies:
                if item.get('name') == 'SUB':
                    result = user + '----' + password + '----\n' + item.get('value') + '\n'
                    with open('cookies.txt', 'a') as f:
                        f.write(result)
                    break
            # print('cookies：', cookies)
            time.sleep(2)
            browser.quit()
            return True
    except:
        print('跳出异常')
        pass

    while True:
        try:
            print('进入手机号界面')
            time.sleep(3)
            phone = getphone()
            browser.find_elements_by_xpath(
                "//div[@class='focus open-blog-phone-border']/input | //div[@class='open-blog-phone-border']/input")[
                0].clear()
            browser.find_elements_by_xpath(
                "//div[@class='focus open-blog-phone-border']/input | //div[@class='open-blog-phone-border']/input")[
                0].send_keys(phone)
            time.sleep(3)
            html = browser.page_source
            sel = etree.HTML(html)
            error = sel.xpath("//p[@id='blogPhoneNumError']/text()")[0]
            print(error)
            if len(error) > 1 or error != '名称不能为空':
                continue
        except:
            print(phone)
            time.sleep(3)
            html = browser.page_source
            sel = etree.HTML(html)
            messaging = sel.xpath("//div[@class='send-msg-tip']/p/text()")
            if len(messaging) == 0:
                continue
            message_content = messaging[0].split('送')[1].split('到')[0]
            addressee = messaging[0].split('到')[1].split('进')[0]

            print(message_content)
            print(addressee)

            phone = putSentMessage(phone, message_content, addressee)
            if phone == -1:
                continue
            flag = getSentMessageStatus(phone)
            if flag:
                browser.find_elements_by_xpath("//input[@id='blogPhoneNum']")[0].clear()
                browser.find_elements_by_xpath("//input[@id='blogPhoneNum']")[0].send_keys(phone)
            else:
                break
    browser.find_elements_by_xpath("//a[@class='btn']")[0].click()
    time.sleep(2)
    browser.quit()
    time.sleep(3)
    return True

class MyFrame(wx.Frame):
    def __init__(self, member_id):
        wx.Frame.__init__(self, None, -1, title="Gui Test Editor", pos=(250, 10), size=(1000, 800))
        self.member_id = member_id

        #创建面板
        frame = wx.Panel(self)
        # wx.Frame.__init__(self, None, -1, u'这是Static Text Example', size=(400, 300))

        self.path_text = wx.TextCtrl(frame, pos=(5, 5), size=(330, 24))
        self.open_button = wx.Button(frame, label="打开", pos=(350, 5), size=(50, 24))
        self.open_button.Bind(wx.EVT_BUTTON, self.openfile)  # 绑定打开文件事件到open_button按钮上
#
        self.save_button = wx.Button(frame, label="存入数据库", pos=(410, 5), size=(70, 24))
        self.save_button.Bind(wx.EVT_BUTTON, self.save_blog)

        self.content_text = wx.TextCtrl(frame, pos=(5, 39), size=(475, 160), style=wx.TE_MULTILINE)
        wx.StaticText(frame, -1, "数据库已存在数据",(15, 210))
        self.repeat = wx.TextCtrl(frame, pos=(5, 235), size=(475, 160), style=wx.TE_MULTILINE)
        self.repeat.SetValue('暂无')
        self.search_button = wx.Button(frame, label="查询数据库数据", pos=(5, 400), size=(100, 24))
        self.search_button.Bind(wx.EVT_BUTTON, self.search_data)  # 绑定打开文件事件到open_button按钮上
        wx.StaticText(frame, -1, "数据库成功数据", (7, 425))
        self.db_success_text = wx.TextCtrl(frame, pos=(5, 450), size=(475, 130), style=wx.TE_MULTILINE)
        wx.StaticText(frame, -1, "数据库失败数据", (15, 590))
        self.db_failed_text = wx.TextCtrl(frame, pos=(5, 610), size=(475, 130), style=wx.TE_MULTILINE)
        wx.StaticText(frame, -1, "请输入开启线程数量", (500, 9))
        self.start_count = wx.TextCtrl(frame, pos=(615, 5), size=(50, 24))
        self.start_count.SetValue('1')

        self.loop = asyncio.get_event_loop()
        self.start_button = wx.Button(frame, label="运行未注册数据", pos=(680, 5), size=(150, 24))
        self.start_button.Bind(wx.EVT_BUTTON, self.open_thread)

        self.start_button = wx.Button(frame, label="运行失败数据", pos=(680, 30), size=(150, 24))
        self.start_button.Bind(wx.EVT_BUTTON, self.open_failed_thread)

        self.stop_button = wx.Button(frame, label="停止", pos=(880, 5), size=(70, 24))
        self.stop_button.Bind(wx.EVT_BUTTON, self.stop)

        self.export_button = wx.Button(frame, label="导出", pos=(880, 30), size=(70, 24))
        self.export_button.Bind(wx.EVT_BUTTON, self.export)


        wx.StaticText(frame, -1, "成功账户信息", (500, 50))
        self.success_info = wx.TextCtrl(frame, pos=(500, 100), size=(475, 300), style=wx.TE_MULTILINE)
        wx.StaticText(frame, -1, "失败账户信息", (500, 430))
        self.failed_info = wx.TextCtrl(frame, pos=(500, 450), size=(475, 300), style=wx.TE_MULTILINE)

    def stop(self, event): # 修改flag状态
        global flag
        flag = True
        print(flag)
        if flag:
            dlg = wx.MessageDialog(None, "停止成功，将运行完该次账户后终止程序", u"提示")
            dlg.ShowModal()
        else:
            dlg = wx.MessageDialog(None, "停止失败", u"提示")
            dlg.ShowModal()

    def export(self, event):  # 定义打开文件事件
        format="%Y-%m-%d %H:%M:%S"
        data_time = datetime.datetime.now().strftime(format)
        success_result = self.success_info.GetValue()
        failed_result = self.failed_info.GetValue()
        file_name = str(int(time.time())) + '.txt'
        with open(file_name, 'w', encoding="utf-8") as f:
            content = data_time + '\n' + '成功帐号信息：' + '\n' + success_result + '\n' + '失败帐号信息：' + '\n' + failed_result
            f.write(content)
        dlg = wx.MessageDialog(None, "导出成功，此次文件名为："+file_name, u"信息")
        dlg.ShowModal()


    def openfile(self, event):  # 定义打开文件事件
        dlg = wx.FileDialog(self, u"选择文件", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.path_text.SetValue(dlg.GetPath())
            path = self.path_text.GetValue()
            with open(path, "r", encoding="utf-8") as f:  # encoding参数是为了在打开文件时将编码转为utf8
                self.content_text.SetValue(f.read())

    def save_blog(self, event):
        db = connect_db()
        info = self.content_text.GetValue().split('\n')
        count = 0
        repeat_list = ''
        for item in info:
            print(item.replace('卡号：', ''))
            result = item.replace('卡号：', '').split('----')
            if len(result) == 3:
                conn = db.cursor()  # 获取指针以操作数据库
                user = result[0]
                sql = 'SELECT user FROM blog where user=%s' % user
                conn.execute(sql)
                repeat_result = conn.fetchone()
                if repeat_result:
                    repeat_list += item + '\n'
                    continue
                password = result[1]
                name = result[2]
                status = 0
                t = [user, password, name, status, self.member_id]
                sql = u"INSERT INTO blog(user,password,name,status, member_id) VALUES (%s,%s,%s,%s,%s)"
                conn.execute(sql, t)
                db.commit()  # 提交操作
                count += 1
        db.close()

        # print(count)
        self.repeat.SetValue(repeat_list)
        dlg = wx.MessageDialog(None, "成功插入数据："+str(count), u"信息")
        dlg.ShowModal()

    def search_data(self, event):
        db = connect_db()
        conn = db.cursor()  # 获取指针以操作数据库
        sql = 'SELECT * FROM blog where status=0 and member_id=%d' % self.member_id
        conn.execute(sql)
        todo_result = conn.fetchall()
        wx.StaticText(wx.Panel(self), -1, '数据库中待注册账户数量：' + str(len(todo_result)), (130, 425))
        sql = 'SELECT * FROM blog where status=1 and member_id=%d' % self.member_id
        conn.execute(sql)
        success_result = conn.fetchall()
        if len(success_result) == 0:
            self.db_failed_text.SetValue('暂无')
        else:
            success_result_list = ''
            for item in success_result:
                info = str(item[0]) + '----' + str(item[1]) + '----' + str(item[2])
                success_result_list += info + '\n'
            self.db_success_text.SetValue(success_result_list)
        sql = 'SELECT * FROM blog where status=-1 and member_id=%d' % self.member_id
        conn.execute(sql)
        failed_result = conn.fetchall()
        db.close()
        if len(failed_result) == 0:
            self.db_failed_text.SetValue('暂无')
        else:
            failed_result_list = ''
            for item in failed_result:
                info = str(item[0]) + '----' + str(item[1]) + '----' + str(item[2])
                failed_result_list += info + '\n'
            self.db_failed_text.SetValue(failed_result_list)

    # def open_asyncio(self, event):
    #     now = lambda: time.time()
    #     start = now()
    #     coroutine = self.open_thread()
    #     # 创建一个事件loop
    #     loop = asyncio.get_event_loop()
    #     # 创建一个task
    #     task = asyncio.ensure_future(coroutine)
    #     print(task)
    #     # 增加一个回调函数
    #     task.add_done_callback(self.callback)
    #     print(task)
    #     loop.run_until_complete(task)
    #     print("Time:", now() - start)
    #
    # def callback(self, future):
    #     print("callback:", future.result())

    def open_thread(self, event):
        global flag
        flag = False
        use_times = self.start_count.GetValue()
        if use_times == '':
            dlg = wx.MessageDialog(None, "请输入开启线程数", u"提示")
            dlg.ShowModal()
            return
        if int(use_times) >= 10:
            dlg = wx.MessageDialog(None, "请将线程数控制在10以内", u"提示")
            dlg.ShowModal()
            return
        # cardcode = CardCode()
        # result = cardcode.__vaild__(b'pin.png')
        # print(use_times)
        # card_number = []
        # with open('blog.txt', 'r') as f:
        #     for i in f.readlines():
        #         card_number.append(i.replace('卡号:', '').strip())
        # sql = 'SELECT user,password,name  FROM blog WHERE status=0 ORDER BY id LIMIT %d' % int(use_times)

        db = connect_db()
        conn = db.cursor()  # 获取指针以操作数据库
        sql = 'SELECT user,password,name  FROM blog WHERE status=0 and member_id=%d ORDER BY id' % self.member_id
        conn.execute(sql)
        blog_list = conn.fetchall()
        db.close()

        if len(blog_list) == 0:
            dlg = wx.MessageDialog(None, "数据库暂无可注册账户信息，请添加", u"提示")
            dlg.ShowModal()
            return

        executor = ThreadPoolExecutor(max_workers=1)
        # # user_id = get_uuid(32)
        # # mac_site = get_mac_address()
        # print('开启线程')
        # while True:
        executor.submit(open_start_thread, self.success_info, self.failed_info, self.member_id, use_times)
        time.sleep(3)

    def open_failed_thread(self, event):
        global flag
        flag = False
        use_times = self.start_count.GetValue()
        if use_times == '':
            dlg = wx.MessageDialog(None, "请输入开启线程数", u"提示")
            dlg.ShowModal()
            return
        if int(use_times) >= 10:
            dlg = wx.MessageDialog(None, "请将线程数控制在10以内", u"提示")
            dlg.ShowModal()
            return
        db = connect_db()
        conn = db.cursor()  # 获取指针以操作数据库
        sql = 'SELECT user,password,name  FROM blog WHERE status=-1 and member_id=%d ORDER BY id' % self.member_id
        conn.execute(sql)
        blog_list = conn.fetchall()
        db.close()

        if len(blog_list) == 0:
            dlg = wx.MessageDialog(None, "数据库暂无失败数据", u"提示")
            dlg.ShowModal()
            return

        executor = ThreadPoolExecutor(max_workers=1)
        status = -1
        executor.submit(open_start_thread, self.success_info, self.failed_info, self.member_id, use_times, status)
        time.sleep(3)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

#
# 　　　┏┓　　　┏┓
# 　　┏┛┻━━━┛┻┓
# 　　┃　　　　　　　 ┃
# 　　┃　　　━　　　 ┃
# 　　┃　┳┛　┗┳　┃
# 　　┃　　　　　　　 ┃
# 　　┃　　　┻　　　 ┃
# 　　┃　　　　　　　 ┃
# 　　┗━┓　　　┏━┛Codes are far away from bugs with the animal protecting
# 　　　　┃　　　┃    神兽保佑,代码无bug
# 　　　　┃　　　┃
# 　　　　┃　　　┗━━━┓
# 　　　　┃　　　　　 ┣┓
# 　　　　┃　　　　 ┏┛
# 　　　　┗┓┓┏━┳┓┏┛
# 　　　　　┃┫┫　┃┫┫
# 　　　　　┗┻┛　┗┻┛
