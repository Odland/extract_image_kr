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

    # 获取帖子对应的源码
    post_source = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="activities"]/div[2]/div/div')))
    post_source_soup = BeautifulSoup(post_source.get_attribute('innerHTML'), 'lxml')

    post_lists = []
    # 博主帖子的链接
    for i in post_source_soup.find_all("a",attrs={"class":"move-to-fullview op-style-modal","href":True,"target":"_blank"}):
        post_lists.append("https://www.styleshare.kr/"+i.get("href"))

    img_urls=[]
    # 获取当前目录
    p = os.getcwd()
    # 匹配url里的数字
    pc  = re.compile(r'(?<=\/)\d+(?=\/)')
    # 博主的名字
    blogger = re.compile(r'(?<=users/).*')
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
            print(img_url)
            img_urls.append(img_url)
    
    if 100  <= len(img_urls) :
        os.mkdir("Image/"+blogger.search(link).group()+"_"+str(len(img_urls)))
        dire = "Image/"+blogger.search(link).group()+"_"+str(len(img_urls))
        print("建立博主的目录是",dire)
        
        for url in img_urls:
            # save_image(url,p + "/Image/" + blogger.search(link).group()+"_"+str(len(img_urls)) + pc.search(url).group() + ".jpeg") 
            save_image(url, os.path.abspath( dire +"/"+ pc.search(url).group() + ".jpeg")) 
        print("目录是",os.path.abspath("Image/"+blogger.search(link).group()+"_"+str(len(img_urls))))






# import requests



# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
# socket.socket = socks.socksocket
# proxies=  {
#     "http": "socks5://127.0.0.1:1080",
#     'https': 'socks5://127.0.0.1:1080'
# }



# for ur in sss:
#     # with open("urls", "a") as f:
#     #     f.write(ur)

#     c=re.search(r"\d+",ur).group()
#     r = requests.get(ur,  proxies=proxies)
#     with open('gpwjd8079'+pc.search(ur)+'.jpeg', 'wb') as f:
#         f.write(r.content)
#         print('文件保存成功')


if __name__ == "__main__":
    crawl_image("https://www.styleshare.kr/users/sss118")