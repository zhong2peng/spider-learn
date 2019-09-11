import argparse
import urllib
import os
import requests
from MyThread import MyThread
from urllib import  request
from bs4 import BeautifulSoup


def get_html(url_address):
    """
    通过url_address得到网页内容
    :param url_address: 请求的网页地址
    :return: html
    """
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 115Browser/9.1.0',
               'Referer':'https://avmoo.asia/cn'}
    req = urllib.request.Request(url=url_address, headers=headers)
    return urllib.request.urlopen(req)

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
    lis = soup.find(id="waterfall").findAll(name='a', attrs={'class':'movie-box'}) # findAll(name='a') # attrs={'class':'lazy'}
    if None != lis:
        img_dirs = {};
        for li in lis:
            # links = li.find('a')
            links = li
            k = links.find('img').attrs['title']
            t = links.attrs['href']
            img_dirs[k] = t;
        print(img_dirs)
        return img_dirs

def download_imgs(info):
    if None == info:
        return
    # 目录
    t = info[0]
    # 地址
    l = info[1]
    if None == t or None == l:
        return
    print("创建相册：" + t +" " + l)
    try:
        os.mkdir(t)
    except Exception as e:
        print("文件夹："+t+"，已经存在")

    print("开始获取相册《" + t + "》内，图片的数量...")

    dir_html = get_html(l)
    dir_soup = get_soup(dir_html)
    # img_page_url = get_dir_img_page_url(l, dir_soup)

    # 得到当前相册的封面
    main_image = dir_soup.findAll(name='a', attrs={'class':'bigImage'})
    if None != main_image:
        for image_parent in main_image:
            imgs = image_parent.findAll(name='img')
            if None != imgs:
                img_url = str(imgs[0].attrs['src'])
                filename = img_url.split('/')[-1]
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(t, filename, img_url, l)

    # # 获取相册下的图片
    # for photo_web_url in img_page_url:
    #     download_img_from_page(t, photo_web_url)



def download_img_from_page(t, page_url):
    dir_html = get_html(page_url)
    dir_soup = get_soup(dir_html)

    # 得到当前页面的图片
    main_image = dir_soup.findAll(name='div', attrs={'class':'main-image'})
    if None != main_image:
        for image_parent in main_image:
            imgs = image_parent.findAll(name='img')
            if None != imgs:
                img_url = str(imgs[0].attrs['src'])
                filename = img_url.split('/')[-1]
                print("开始下载:" + img_url + ", 保存为："+filename)
                save_file(t, filename, img_url, '')



def save_file(d, filename, img_url, refer):
    print(img_url+"=========")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 115Browser/9.1.0',
        'Referer': refer}
    keyword = ''
    img = requests.get(img_url, params=keyword, headers=headers, timeout=3)
    name = str(d+"/"+filename)
    with open(name, "wb") as code:
        code.write(img.content)

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
    # parser = argparse.ArgumentParser()
    # parser.add_argument("echo")
    # parser.add_argument("url")
    # url = int(args.url)
    # args = parser.parse_args()
    # url = str(args.echo)
    url = "https://avmoo.asia/cn"
    print("开始解析：" + url)

    html = get_html(url)
    soup = get_soup(html)
    img_dirs = get_img_dirs(soup)
    if None == img_dirs:
        print("无法获取该网页下的相册内容...")
    else:
        for d in img_dirs:
            # print(img_dirs.get(d))
            # download_imgs((d, img_dirs.get(d)))
            my_thread = MyThread(download_imgs, (d, img_dirs.get(d)))
            my_thread.start()
            my_thread.join()