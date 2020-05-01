from bs4 import BeautifulSoup
import requests
import re
import time
import sys
import os
from contextlib import closing
import random

url = 'https://www.styleshare.kr/users/ahw59'

headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'x-newrelic-id': 'UAcDV1dbGwIJVlFWDwY=',
        'x-requested-with': 'XMLHttpRequest',
    }



def save_image(url,filename):
    """请求链接保存图片"""
    # 请求超时重新请求
    flag = True
    while flag:
        try:
            with closing(requests.get(url, stream=True,timeout=(7, 20))) as r:
                # time.sleep(random.randint(2,5)/10)
                flag = False
                with open(filename, 'wb') as f:
                    for data in r.iter_content(1024):
                        f.write(data)
                    # print("文件保存成功!")
        except requests.exceptions.ReadTimeout as e:
            print(e)
            print("保存图片时读取超时了")
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print("保存图片时连接超时了")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("保存图片时超时了")




def extract_images(image_link_num, user_link, post_id):
    """获取一个帖子的所有图片"""
    p = re.compile(r'(?<=users/).*')
    # 请求的url
    url = base_url + p.search(user_link).group() + "/" + post_id
    # referer
    headers["referer"] = url
    # time.sleep(random.randint(2, 5) / 10)
    flag = True
    while flag:
        try:
            r = requests.get(url, headers=headers, timeout=(10, 40))
            flag = False
        except requests.exceptions.ReadTimeout as e:
            print(e)
            print("获取帖子时读取超时了")
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print("获取帖子时连接超时了")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("获取帖子时连接错误")
    # print("帖子的链接",url)
    images = BeautifulSoup(r.text, "lxml")
    # 获取包含图片链接的元素
    image_links = images.find_all("figure", attrs={"class": True, "id": False})
    if len(image_links) == 0:
        image_links = images.find_all(
            "div", attrs={"class": "pictures op-carousel"})
    # print("长度是",len(image_links))
    imaglist = []
    for i in image_links:
        try:
            link = re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src"))
        except AttributeError as e:
            print("遇到错误", e)
            print("continue,链接是", i)
            continue
        # print(re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src")))
        # print("图片链接",link)
        imaglist.append(link)
        # print("运行了")
        image_link_num.append(link)
    # print("这个帖子的图片数量", len(imaglist))


def run(blogger,images):

    params = {
        "limit": "30",
        "offset": "0",
    }
    p = re.compile(r'(?<=users/).*')
    pc = re.compile(r'(?<=\/)\d+(?=\/)')

    user_link = 'https://www.styleshare.kr/users/'+blogger
    headers["referer"] = user_link
    base_url = "https://www.styleshare.kr/"
    url = base_url + blogger + "/styles"
    # print("请求一个博主的所有的帖子的url是",url)
    # 获取所有的帖子
    list_temp = []
    # 循环获取所有的帖子
    for n in range(20):
        params["offset"] = str(n * 30)
        # time.sleep(random.randint(2, 5) / 10)
        flag = True
        while flag:
            try:
                r = requests.get(url, params=params,
                                headers=headers, timeout=(10, 40))
                flag = False
            except requests.exceptions.ReadTimeout as e:
                print(e)
                print("获取帖子id时读取超时了")
            except requests.exceptions.ConnectTimeout as e:
                print(e)
                print("获取帖子id时连接超时了")
            except requests.exceptions.ConnectionError as e:
                print(e)
                print("获取帖子id时连接错位")
        post_html = BeautifulSoup(r.text, "lxml")
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
        print("这个博主总共的帖子数是", len(list_temp))
    image_links = []
    print("正在获取博主的图片数量...")
    numb = 0
    for post_id in list_temp:
        extract_images(image_links, user_link, post_id)
        numb += 1
        if numb > 30 and numb % 30 == 0:
            print("现在获取的是第{}张图片".format(numb))

    print("总的图片数", len(image_links))
    dire = "beauty/" + p.search(user_link).group()
    try:
        os.makedirs(dire) 
    except FileExistsError :
        print("已经创建文件,抓取过了")
        return
    # dire = "beauty/" + p.search(user_link).group() 
    print("开始存储图片,存储博主图片的目录是", dire)
    image_num = 0
    for image_link in image_links:
        if not pc.search(image_link).group() in images:
            print("存储的是",pc.search(image_link).group())
            save_image(image_link,os.path.abspath(
                dire +"/"+ pc.search(image_link).group() + ".jpeg"))
            image_num += 1
            if image_num > 30 and image_num % 30 == 0:
                print("正在存储第{}张图片".format(image_num))
    # print("抓取完毕,这是第{}张图片".format(len(image_links)))


  

def extract_images(image_link_num, user_link, post_id):
    """获取一个帖子的所有图片"""
    p = re.compile(r'(?<=users/).*')
    # 请求的url
    base_url = "https://www.styleshare.kr/"
    url = base_url + p.search(user_link).group() + "/" + post_id
    # referer
    headers["referer"] = url
    # time.sleep(random.randint(2, 5) / 10)
    flag = True
    while flag:
        try:
            r = requests.get(url, headers=headers, timeout=(10, 40))
            flag = False
        except requests.exceptions.ReadTimeout as e:
            print(e)
            print("获取帖子时读取超时了")
        except requests.exceptions.ConnectTimeout as e:
            print(e)
            print("获取帖子时连接超时了")
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("获取帖子时连接错误")
    # print("帖子的链接",url)
    images = BeautifulSoup(r.text, "lxml")
    # 获取包含图片链接的元素
    image_links = images.find_all("figure", attrs={"class": True, "id": False})
    if len(image_links) == 0:
        image_links = images.find_all(
            "div", attrs={"class": "pictures op-carousel"})
    # print("长度是",len(image_links))
    imaglist = []
    for i in image_links:
        try:
            link = re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src"))
        except AttributeError as e:
            print("遇到错误", e)
            print("continue,链接是", i)
            continue
        # print(re.sub(r"\d{2}x\d{2}", "640x640", i.img.get("src")))
        # print("图片链接",link)
        imaglist.append(link)
        # print("运行了")
        image_link_num.append(link)
    # print("这个帖子的图片数量", len(imaglist))

def main(dirname='/home/field/Desktop/beauty'):
    for i in os.listdir(dirname):
        print("博主目录名",i)
        images = []
        images = list(map(lambda x:re.search(r'\d+',x).group(),os.listdir(dirname+'/'+i)))
        blogger = re.search(r'.*(?=\_)',i).group()
        print("博主名",blogger)
        if blogger in os.listdir('/home/field/extract_image_kr/beauty'):
            print("已经存在,不再抓取")
            continue
        for n in images:
            print("图片名",n)
        print("类型",type(images))
        run(blogger,images)
        

if __name__ == "__main__":
    main()