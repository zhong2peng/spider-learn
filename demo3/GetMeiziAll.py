import argparse
import urllib
import os
import requests
from MyThread import MyThread
from urllib import  request
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
# 'https://avmoo.asia/cn'
ua = UserAgent()
useragent = ua.random
def get_html(url_address,refer):
    """
    通过url_address得到网页内容
    :param url_address: 请求的网页地址
    :return: html
    """
    ua = UserAgent()
    # headers = {'User-Agent':ua.random, 'Referer': refer}
    headers = {'User-Agent':ua.random
         , 'Referer': refer
               }
    req = urllib.request.Request(url=url_address, headers=headers)
    try:
        return urllib.request.urlopen(req, timeout=120)
    except Exception as e:
        print('[error][get_html]: ' + url_address+', ref: '+refer)
        time.sleep(30)

#
def get_soup(html):
    """
    把网页内容封装到BeautifulSoup中并返回BeautifulSoup
    :param html: 网页内容
    :return:BeautifulSoup
    """
    if None == html:
        return
    return BeautifulSoup(html.read(), "html.parser")


def get_img_dirs(soup):
    """
    获取所有相册标题及链接
    :param soup: BeautifulSoup实例
    :return: 字典（ key:标题， value:内容）
    """
    if None == soup:
        return
    lis = soup.find(name="div",attrs={'class':'container-fluid pt-10'}).findAll(attrs={'class':'col-lg-2 col-md-2 col-sm-3 col-xs-6 text-center'}) # findAll(name='a') # attrs={'class':'lazy'}
    if None != lis:
        img_dirs = {};
        for li in lis:
            k = li.text
            t = li.attrs['href']
            img_dirs[k] = t
        print(img_dirs)
        return img_dirs

def download_imgs(info):
    if None == info:
        return
    # 目录
    t = info[0]
    # 地址
    l = info[1]
    # refer
    refer = info[2]
    if None == t or None == l:
        return
    print("创建相册：" + t +" " + l)
    try:
        os.mkdir(t)
    except Exception as e:
        print("文件夹："+t+"，已经存在")

    print("开始获取相册《" + t + "》内，图片的数量...")

    dir_html = get_html(l, refer)
    dir_soup = get_soup(dir_html)
    # img_page_url = get_dir_img_page_url(l, dir_soup)

    # 得到当前相册的封面
    main_image = dir_soup.find(id='waterfall').findAll(name='div', attrs={'class':'item'})
    rest_image = dir_soup.findAll(name='a', attrs={'name':'nextpage'})[0].attrs['href']
    if None != main_image:
        i=0
        for image_parent in main_image:
            aHref = image_parent.find('a').attrs['href']
            big_html = get_html(aHref, l)
            big_soup = get_soup(big_html)
            big_image = big_soup.find(name='a', attrs={'class':'bigImage'})
            imgs = image_parent.findAll(name='img')
            if None != imgs and None != big_image:
                i = i+1
                # img_url = str(imgs[0].attrs['src']) 小图
                img_url = big_image.attrs['href']
                # filename = img_url.split('/')[-1]
                suffix = img_url.split('/')[-1].split('.')[1]
                filename = image_parent.findAll(name='date')[0].text+'.'+suffix
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(t, filename, img_url, aHref, i)
    # 获取下一页的封面
    if None != rest_image:
        download_imgs(( info[0], 'https://avmoo.asia'+rest_image, l))


    # # 获取相册下的图片
    # for photo_web_url in img_page_url:
    #     download_img_from_page(t, photo_web_url)

def download_all():

    return

def download_img_from_page(t, page_url):
    dir_html = get_html(page_url,'')
    dir_soup = get_soup(dir_html)

    # 得到当前页面的图片
    main_image = dir_soup.findAll(name='div', attrs={'class':'main-image'})
    if None != main_image:
        i = 0
        for image_parent in main_image:
            i = i+1
            imgs = image_parent.findAll(name='img')
            if None != imgs:
                img_url = str(imgs[0].attrs['src'])
                filename = img_url.split('/')[-1]
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(t, filename, img_url, '')



def save_file(d, filename, img_url, refer,i):
    if i%11 == 10:
        time.sleep(10)
    # print(img_url+"=========")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 115Browser/9.1.0',
        'Referer': refer}
    keyword = ''
    try:
        img = requests.get(img_url, headers=headers, timeout=3)
        name = str(d + "/" + filename)
        with open(name, "wb") as code:
            code.write(img.content)
    except Exception as e:
        print('[error]: '+img_url)


def get_dir_img_page_url(l, dir_soup):
    """
    获取相册里面的图片数量
    :param l: 相册链接
    :param dir_soup:
    :return: 相册图片数量
    """
    divs = dir_soup.findAll(name='div', attrs={'class':'pagenavi'})
    navi = divs[0]
    code = navi['class']
    print(code)

    links = navi.findAll(name='a')
    if None == links:
        return
    a = []
    url_list = []
    for link in links:
        h = str(link['href'])
        n = h.replace(l+"/", "")
        try:
            a.append(int(n))
        except Exception as e:
            print(e)
    _max = max(a)
    for i in range(1, _max):
        u = str(l+"/"+str(i))
        url_list.append(u)
    return url_list



if __name__ == '__main__':
    url = "https://avmoo.asia/cn/genre"
    print("开始解析：" + url)

    html = get_html(url, 'https://avmoo.asia/cn')
    soup = get_soup(html)
    img_dirs = get_img_dirs(soup)
    threads = []
    if None == img_dirs:
        print("无法获取该网页下的相册内容...")
    else:
        for d in img_dirs:
            # print(img_dirs.get(d))
            # download_imgs((d, img_dirs.get(d), 'https://avmoo.asia/cn'))
            my_thread = MyThread(download_imgs, (d, img_dirs.get(d), 'https://avmoo.asia/cn'))
            my_thread.start()
            my_thread.join()
        #     threads.append(my_thread)
        # for my in threads:
        #     my.join()