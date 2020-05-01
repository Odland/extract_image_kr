# 爬取韩国美妆博主网站styleshare博主发布的图片

***crawler_kr_selenium.py使用selenium模拟浏览器动作图片***

***extract_image_kr.py 使用requests获取图片数据***

***update_extract_image_kr.py使用requests增量更新图片***

* 程序运行
    * 抓取图片并将获取到的图片以流的方式存储到对应的目录里
    
        `python extract_image_kr.py`

    * 根据已有的美妆博主目录增量更新对应的美妆图片

        `python update_extract_image_kr.py`
