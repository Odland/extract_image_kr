from bs4 import BeautifulSoup
import requests
import re
import time
import sys
import os
from contextlib import closing
import random

import socket
import socks
proxies=  {
    "http": "socks5://127.0.0.1:1080",
    'https': 'socks5://127.0.0.1:1080'
}

base_url = "https://www.styleshare.kr/"
url = ''
headers = {
    'accept': '*/*',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.9',
    'referer':url,
    'sec-fetch-mode':'cors',
    'sec-fetch-site':'same-origin',
    'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'x-newrelic-id':'UAcDV1dbGwIJVlFWDwY=',
    'x-requested-with':'XMLHttpRequest',
}


def save_image(url,filename):
    """请求链接保存图片"""
    # 请求超时重新请求
    flag = True
    while flag:
        try:
            with closing(requests.get(url, stream=True,timeout=(10, 40))) as r:
                # time.sleep(random.randint(2,5)/10)
                flag = False
                with open(filename, 'wb') as f:
                    for data in r.iter_content(1024):
                        f.write(data)
                    print("文件保存成功!")
        except requests.exceptions.ReadTimeout as e:
            print(e)
            print("保存图片时读取超时了")
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print("保存图片时连接超时了")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("保存图片时超时了")


def compare_blogger(bloggername):
    """比对博主是否是已经抓取过的博主"""
    nb = bloggername
    print("nb是",nb)
    nms = set()
    # # 遍历Image目录下的分类子目录
    for nm in os.listdir("Image"):
        # print("nm是",nm)
        # print(os.path.abspath("Image/"+nm))
        # 获取分类目录下的博主名字
        for i in os.listdir(os.path.abspath("Image/"+nm)):
            try:
                nms.add(re.search(r".*(?=\_\d+$)", i).group())
            except AttributeError:
                pass
        print("文件列表", nms)
        # 判断一下博主已经抓取过
        if nb in nms:
            print("重复抓取了博主，直接返回程序")
            print("抓取的这个博主是", nb)
            return True


def extract_blogger(arg = "feed/dailylook"):
    """获取博主主页链接"""
    # http参数
    params={
    "until":str(time.time()).split('.')[0],
    "offset":"0",
    }
    blogger_links = []
    # 设置请求头referer
    headers["referer"] = base_url + arg
    url = base_url + arg
    for i in range(10):
        # 每次获取30个博主
        l = []
        params["offset"]=i*30
        r = requests.get(url,headers=headers,params=params,timeout=(10, 40))
        bloggers_html = BeautifulSoup(r.text,"lxml")
        bloggers = bloggers_html.find_all("figure",class_="profile-picture-wrapper")
        for blogger in bloggers:
            # 获取博主主页链接
            print("https://www.styleshare.kr" + blogger.find("a").get("href"))
            l.append("https://www.styleshare.kr" + blogger.find("a").get("href"))
            blogger_links.append("https://www.styleshare.kr" + blogger.find("a").get("href"))
        # print("\n\n")
        # print("这一页抓取到的博主的主页链接", len(l))
        # print("总共的链接",len(blogger_links))
        # print("i是",i)
    return blogger_links

def extract_images(image_link_num,user_link,post_id):
    """获取一个帖子的所有图片"""
    p = re.compile(r'(?<=users/).*')
    # 请求的url
    url = base_url  + p.search(user_link).group() + "/" + post_id
    # referer
    headers["referer"] = url
    # time.sleep(random.randint(2, 5) / 10)
    flag = True
    while flag:
        try:
            r = requests.get(url, headers=headers,timeout=(10, 40))
            flag = False
        except requests.exceptions.ReadTimeout as e :
            print(e)
            print("获取帖子时读取超时了")
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print("获取帖子时连接超时了")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("获取帖子时连接错位")
    print("帖子的链接",url)
    images = BeautifulSoup(r.text, "lxml")
    # 获取包含图片链接的元素
    image_links = images.find_all("figure", attrs={"class": True, "id": False})
    if len(image_links) == 0 :
        image_links = images.find_all("div",attrs={"class":"pictures op-carousel"})
    print("长度是",len(image_links))
    imaglist = []
    for i in image_links:
        link = re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src"))
        # print(re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src")))
        # print("图片链接",link)
        imaglist.append(link)
        # print("运行了")
        image_link_num.append(link)
    print("这个帖子的图片数量", len(imaglist))







def extract_id():
    """获取博主每个帖子对应的id值"""
    l = ["feed/dailylook",'feed/beauty','feed/new','feed/qna']
    dict_cat = {"feed/dailylook":"Image/clothes/",
                'feed/beauty':"Image/beauty/",
                "feed/new":"Image/other/",
                "feed/qna":"Image/other/",
                "feed/hot":"Image/other/"}
    for arg in l:
        links = extract_blogger(arg)
        print("博主的数量",len(links))
        # 博主的id
        p = re.compile(r'(?<=users/).*')
        pc = re.compile(r'(?<=\/)\d+(?=\/)')
        for user_link in links:
            # 遍历每个博主获取每个帖子的id值
            print("博主的链接",user_link)
            # 避免重复存储同一个博主的图片

            # 得到抓取到的博主的名字
            nb = p.search(user_link).group()
            print("用户名是",nb)
            # 博主在目录里
            if  compare_blogger(nb):
                continue
            params = {
                "limit": "30",
                "offset": "0",
            }
            headers["referer"] = user_link
            url = base_url + p.search(user_link).group() + "/styles"
            print("url是",url)
            # 获取所有的帖子
            list_temp = []
            # 循环获取所有的帖子
            for n in range(10):
                params["offset"] = str(n * 30)
                # time.sleep(random.randint(2, 5) / 10)
                r = requests.get(url,params=params,headers=headers,timeout=(10, 40))
                post_html = BeautifulSoup(r.text,"lxml")
                posts = post_html.find_all("div", attrs={"id": True})
                l = []
                for post in posts:
                    post_id = post.get("data-style-id")
                    # print(post_id)
                    l.append(post_id)
                    list_temp.append(post_id)
                # 没有帖子获取了
                if len(l) == 0:
                    break
                #     print("这一次请求帖子数是",len(l))
                # print("这个博主总共的帖子数是",len(list_temp))
            if len(list_temp) < 12:
                # 认为帖子数低于15的总图片数量小于100
                print("帖子数小于15直接跳过不抓取")
                continue
            image_links = []
            for post_id in list_temp:
                extract_images(image_links,user_link,post_id)
            print("总的图片数",len(image_links))

            if len(image_links) >= 100 :
                # 博主的名字
                os.mkdir(dict_cat[arg] + p.search(user_link).group() + "_" + str(len(image_links)))
                dire = dict_cat[arg] + p.search(user_link).group() + "_" + str(len(image_links))
                print("建立博主的目录是", dire)
                for image_link in image_links:
                    save_image(image_link,os.path.abspath(
                        dire +"/"+ pc.search(image_link).group() + ".jpeg"))



            # break

if __name__ == '__main__':
    extract_id()