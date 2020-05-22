# coding = utf-8
from config import *
import json
import time
import urllib.request
from selenium import webdriver
import datetime
import time
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

global browser_handler


def init_browser():
    global browser_handler
    if SHOW_WINDOW:
        browser_handler = webdriver.Firefox()
        browser_handler.get('http://www.baidu.com')
    else:
        browser_options = Options()
        browser_options.add_argument('--headless')
        browser_handler = webdriver.Firefox(firefox_options=browser_options)
    print("浏览器初始化成功")


def login():
    global browser_handler
    browser_handler.get('https://ielts.neea.cn/')
    time.sleep(2)
    element = browser_handler.find_element_by_id('btn_log_goto')
    element.click()
    time.sleep(2)
    print("官网已打开，开始登陆")
    flag = True
    while flag:
        element = browser_handler.find_element_by_id('userId')
        element.clear()
        element.send_keys(USER_NAME)
        element = browser_handler.find_element_by_id('userPwd')
        element.clear()
        element.send_keys(PASSWORD)
        element = browser_handler.find_element_by_id('loginForm')
        element.click()
        time.sleep(2)
        element = browser_handler.find_element_by_id('chkImg')
        element.click()
        time.sleep(5)
        chk_img_url = element.get_attribute("src")
        with open('chk.jpg', "wb") as f:
            f.write(urllib.request.urlopen(chk_img_url).read())
        time.sleep(20)
        with open('chk.txt', "r") as f:
            chk_str = f.readline()
        element = browser_handler.find_element_by_id('checkImageCode')
        element.clear()
        element.send_keys(chk_str)
        time.sleep(1)
        element = browser_handler.find_element_by_id('btn_log_goto')
        element.click()
        time.sleep(2)
        try:
            browser_handler.find_element_by_id("breadcrumbRange")
            print("登陆成功")
            flag = False
        except Exception as e:
            print("登陆失败")


def alarm(message):
    print('开始发送信息：' + message)
    client = AcsClient(ACCESS_KEY_ID, ACCESS_SECRET, 'cn-hangzhou')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', PHONE_NUMBER)
    request.add_query_param('SignName', "KisPig网")
    request.add_query_param('TemplateCode', "SMS_184215625")
    request.add_query_param('TemplateParam', "{\"message\": \"" + message + "\"}")
    response = client.do_action_with_exception(request)
    print("通知短信%s已发送%s" % (message, response))
    quit()


def inquiry():
    # 查询UKVI
    browser_handler.get('https://ielts.neea.cn/myHome/' + USER_NAME + '/querySeat?productId=IELTSUKVI')
    bs = BeautifulSoup(browser_handler.page_source, "html.parser")
    for x in bs.find_all('input', attrs={'type': 'checkbox'}):
        for y in UKVI_INQUIRY:
            if x.get('value') == y:
                alarm(y[-2:] + 'UKVI')
                return
    # 查询PBT
    url = 'https://ielts.neea.cn/myHome/' + USER_NAME + '/querySeat?productId=IELTSPBT&_=' + str(int(round(time.time() * 1000))) + '&2a9lhcMh=' + browser_handler.get_cookie('1laYpfWboXsu443T')['value']

    browser_handler.get(str(url))
    for month in PBT_INQUIRY:
        for p in PBT_INQUIRY[month]:
            import pdb
            pdb.set_trace()
            url = 'https://ielts.neea.cn/myHome/' + USER_NAME + '/queryTestSeats?queryMonths=' + month + '&queryProvinces=' + str(
                p['value']) + '&neeaAppId=&productId=IELTSPBT&levelCode=&_=' + str(
                int(round(time.time() * 1000))) + '&2a9lhcMh=' + browser_handler.get_cookie('1laYpfWboXsu443T')['value']

            browser_handler.get(str(url))
            bs = BeautifulSoup(browser_handler.page_source, "html.parser")
            response = json.loads(bs.text)
            for date in response:
                for diDian in response[date]:
                    if (diDian['seatStatusCn'] != '名额暂满'):
                        alarm(p['province'] + month[-2:] + 'PB')
                        return


if __name__ == "__main__":
    init_browser()
    login()

    start_time = datetime.datetime.now()
    num = 0
    while True:
        last_time = (datetime.datetime.now() - start_time).seconds
        num = num + 1
        # print('************   上轮用时 %d 秒，开始第 %d 遍查询    ************' % (last_time, num))
        print(num)
        start_time = datetime.datetime.now()
        browser_handler.get('https://ielts.neea.cn/myHome/' + USER_NAME + '/homepage')
        inquiry()
        time.sleep(5)
