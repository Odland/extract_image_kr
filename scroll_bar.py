import sys
import os
import shutil
import re
import datetime
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging


import socket
import socks

from contextlib import closing
import requests


# 设置代理
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--proxy-server=socks5://localhost:1080')
browser=webdriver.Chrome(options=chrome_options)
browser.maximize_window()

proxies=  {
    "http": "socks5://127.0.0.1:1080",
    'https': 'socks5://127.0.0.1:1080'
}

def down_():

    browser.get("https://www.styleshare.kr/users/yeonavu")
    time.sleep(3)

    # 判断一下帖子的数量
    num_str = browser.find_element_by_css_selector("#activities > div.op-content-cards.style-cards.op-style-cards > p")
    print(num_str.text)
    num = re.search(r"\d+",num_str.text).group()
    print(int(num))
    num = int(num)
    # 如果帖子数小于15就没必要抓取来了
    if num < 15:
        print("不爬") 
    # 帖子数大于30就得下拉滚动条
    elif num > 30:
        # 滑动时每次都得递增
        down_num =  num // 30    
        browser.execute_script("window.scrollTo(0,2000);")
        print("滑动一下")
        time.sleep(3)
        print("再滑动一下")
        browser.execute_script("window.scrollTo(0,3000);")
        time.sleep(3)
        print("再再滑动一下")
        browser.execute_script("window.scrollTo(0,4000);")


# 获取博主链接
# 打开首页
url = 'https://www.styleshare.kr/feed/new'
browser.get(url)
time.sleep(3)

# 找到末尾的元素，若找不到，就说明加载完了
# 滑动滚动条
for _ in range(20):
    try:
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((
                By.CSS_SELECTOR,'#filter-board > div > div.card-sheet.op-card-wrapper.pos-relative > div.op-load-more-trigger.op-fluid-card.left.pos-absolute.op-watching-target.in')))
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(5)
    except selenium.common.exceptions.TimeoutException as e:
        # 找不到元素的情况
        break

# 获取博主主页链接
blogger_xp = '//*[@id="filter-board"]/div/div[1]'
divs = browser.find_element_by_xpath(blogger_xp)
blogger_divs = BeautifulSoup(divs.get_attribute('innerHTML'), 'lxml')
bloggers = blogger_divs.find_all("div",attrs={"id":True,"data-style-id":True})
l = []
for blogger in bloggers:
    a = blogger.find("figure",class_="profile-picture-wrapper").a.get("href")
    print(a)
    l.append(a)
print(len(l))