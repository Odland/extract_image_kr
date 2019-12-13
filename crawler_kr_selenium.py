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




def save_image(url,filename):
    """请求链接保存图片"""
    with closing(requests.get(url, stream=True,proxies = proxies)) as r:
        with open(filename, 'wb') as f:
            for data in r.iter_content(1024):
                f.write(data)
            print("文件保存成功!")




def crawl_image(link):
    """抓取每个博主的图片"""
    # link = 'https://www.styleshare.kr/users/260.st'
    browser.get(link)
    time.sleep(3)

    # 判断一下帖子的数量
    # 遇到404的情况
    try:
        num_str = browser.find_element_by_css_selector("#activities > div.op-content-cards.style-cards.op-style-cards > p")
    except selenium.common.exceptions.NoSuchElementException:
        return
    # print(num_str.text)
    num = re.search(r"\d+",num_str.text).group()
    # print(int(num))
    num= int(num)
    # 如果帖子数小于15就没必要抓取来了
    if num < 20:
        return 
    # 帖子数大于30就得下拉滚动条
    elif num > 30:
        down_num =  num // 30 
        for _ in range(down_num):
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2) 
    # 去重，将已经存储过的博主剔除   
    # 博主的名字
    blogger = re.compile(r'(?<=users/).*')
    # 得到抓取到的博主的名字
    nb = blogger.search(link)
    nms = set()
    # 从目录里提取所有以博主的名字命名的目录
    for nm in os.listdir("Image"):
        try:
            nms.add(re.search(r"\w+\_\d+$",nm).group())
        except AttributeError :
            pass
    if nb in nms:
        print("重复抓取了博主，直接返回程序")
        return 

    # 获取帖子对应的源码
    post_source = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="activities"]/div[2]/div/div')))
    post_source_soup = BeautifulSoup(post_source.get_attribute('innerHTML'), 'lxml')

    post_lists = []
    # 博主帖子的链接
    for i in post_source_soup.find_all("a",attrs={"class":"move-to-fullview op-style-modal","href":True,"target":"_blank"}):
        post_lists.append("https://www.styleshare.kr"+i.get("href"))

    img_urls=[]
    # 获取当前目录
    p = os.getcwd()
    # 匹配url里的数字
    pc  = re.compile(r'(?<=\/)\d+(?=\/)')
    # 遍历所有帖子里的图片
    for i in post_lists:
        browser.get(i)
        # 获取一个帖子里的所有连接
        try:
            l = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,'/html/body/section[1]/div/div[1]/div[2]/div')))
        except selenium.common.exceptions.TimeoutException:
            l = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,'/html/body/section[1]/div/div[1]/div[1]')))
        img_all_soup = BeautifulSoup(l.get_attribute('innerHTML'), 'lxml')
        
        for img in img_all_soup.find_all("img"):
            # 替换链接
            img_temp = img.get("src")
            img_url = img_temp.replace("50x50","640x640")
            # print(img_url)
            img_urls.append(img_url)
    
    if 100  <= len(img_urls) :
        os.mkdir("Image/"+blogger.search(link).group()+"_"+str(len(img_urls)))
        dire = "Image/"+blogger.search(link).group()+"_"+str(len(img_urls))
        print("建立博主的目录是",dire)
        
        for url in img_urls:
            # save_image(url,p + "/Image/" + blogger.search(link).group()+"_"+str(len(img_urls)) + pc.search(url).group() + ".jpeg") 
            save_image(url, os.path.abspath( dire +"/"+ pc.search(url).group() + ".jpeg")) 
        print("目录是",os.path.abspath("Image/"+blogger.search(link).group()+"_"+str(len(img_urls))))



def excract_logger_link(url):
    """抓取博主首页的链接"""
    # 打开首页
    # url = 'https://www.styleshare.kr/feed/beauty'
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
        # print(a)
        l.append('https://www.styleshare.kr'+a)
    return l

if __name__ == "__main__":
    links = ['https://www.styleshare.kr/feed/hot','https://www.styleshare.kr/feed/dailylook','https://www.styleshare.kr/feed/beauty',
    'https://www.styleshare.kr/feed/new','https://www.styleshare.kr/feed/qna']
    for link in links:
        # 先抓取每个模块的所有博主的主页链接
        url = excract_logger_link(link)
        # 遍历博主主页链接
        for i in url:
           crawl_image(i) 
