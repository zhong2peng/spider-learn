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

def get_html(url_address,refer,time_obj):
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
        return urllib.request.urlopen(req, timeout=180)
    except Exception as e:
        if None != time_obj and time_obj[0] < 3:
            time.sleep(3)
            print("[get_html][retry]:"+str(time_obj[0]))
            return get_html(url_address, refer, [(time_obj[0]+1)])
        else:
            print('[error][get_html]: ' + url_address+', ref: '+refer)
            time.sleep(3)

#
def get_soup(html):
    """
    把网页内容封装到BeautifulSoup中并返回BeautifulSoup
    :param html: 网页内容
    :return:BeautifulSoup
    """
    if None == html:
        return
    try:
        return BeautifulSoup(html.read(), "html.parser")
    except Exception as e:
        print('[error][get_soup]: ')
        time.sleep(3)


def get_img_dirs(soup):
    """
    获取所有相册标题及链接
    :param soup: BeautifulSoup实例
    :return: 字典（ key:标题， value:内容）
    """
    if None == soup:
        return
    lis = soup.find(id='waterfall').findAll(name='div', attrs={'class':'item'}) # findAll(name='a') # attrs={'class':'lazy'}
    if None != lis:
        img_dirs = {};
        for li in lis:
            k = li.find(name='div',attrs={'class':'photo-info'}).find(name='span').text
            t = li.find('a').attrs['href']
            img_dirs[k] = t
        print(img_dirs)
        return img_dirs

def download_thumb_list(big_soup, t, refer,i):
    """
    获取所有相册标题及链接
    :param soup: BeautifulSoup实例
    :return: 字典（ key:标题， value:内容）
    """
    if None == big_soup:
        return
    # 得到当前相册的封面
    big_image = big_soup.find(name='a', attrs={'class': 'bigImage'})
    if None != big_image:
        img_url = big_image.attrs['href']
        suffix = img_url.split('/')[-1].split('.')[1]
        pic_no = big_soup.find(name='div', attrs={'class':'col-md-3 info'}).find(name = 'p').findAll(name='span')[1].text
        filename = pic_no + '.' + suffix
        print("开始下载:" + img_url + ", 保存为：" + filename)
        save_file(t, filename, img_url, refer, i,[0])

def download_imgs(info):
    if None == info:
        return
    # 目录
    t = info[0]
    if t == '波多野結衣':
        return
    # 地址
    l = info[1]
    # refer
    refer = info[2]
    # start_page
    start_page = info[3][0]
    original_url = info[3][1]

    if None == t or None == l:
        return
    print("创建相册：" + t +" " + l)
    try:
        os.mkdir(t)
    except Exception as e:
        print("文件夹："+t+"，已经存在")

    # 获取女星当前page地址名称 + 缩略图链接的map表
    lis = get_current_thumbs_list(l, refer)
    if None != lis:
        j = 1
        for li in lis:
            if 1 == j:
                j = j + 1
                continue
            j = j + 1
            if j % 31 == 30:
                time.sleep(1)
            third_url = lis.get(li)
            # 作品详情图的soup
            download_thumb_list(get_current_html_soup(third_url, l), t, third_url, j)
        print('[download]' + t + ':' + str(start_page + 1))
        download_imgs((
                      info[0], original_url + '/page/' + str(start_page + 1), original_url + '/page/' + str(start_page),
                      [start_page + 1, original_url]))
    else:
        return

def save_file(d, filename, img_url, refer,i,time_obj):
    if i%11 == 10:
        time.sleep(10)
    # print(img_url+"=========")
    ua = UserAgent()
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36 115Browser/9.1.0',
        'User-Agent': ua.random,
        'Referer': refer}
    try:
        img = requests.get(img_url, headers=headers, timeout=3)
        name = str(d + "/" + filename)
        with open(name, "wb") as code:
            code.write(img.content)
    except Exception as e:
        time.sleep(3)
        if None != time_obj and time_obj[0] <1:
            save_file(d, filename, img_url, refer, i, [(time_obj[0]+1)])
        else:
            print('[error]: '+img_url)

def get_current_thumbs_list(url, refer):
    html = get_html(url, refer,[0])
    soup = get_soup(html)
    if None == soup:
        print('[get_current_thumbs_list]: '+url+' ,'+refer)
        return
    return get_img_dirs(soup)

def get_current_html_soup(url, refer):
    dir_html = get_html(url, refer,[0])
    res = get_soup(dir_html)
    if None == res:
        print('[get_current_html_soup]: '+url+' ,'+refer)
    return res

def consume_last(i_dir):
    h_map = {'AIKA','JULIA','あおいれな','あべみかこ','きみと歩実','つぼみ','三原ほのか','三島奈津子','二階堂ゆり','佐々木あき',
             '佐々波綾','優月まりな','吉沢明歩','吹石れな','大槻ひびき','川上ゆう（森野雫）','川上奈々美','希崎ジェシカ',
             '推川ゆうり','春菜はな','松本菜奈実','栄川乃亜','森沢かな（飯岡かなこ）','椎名そら','水野朝陽','波多野結衣','波木はるか',
             '浜崎真緒','澁谷果歩','澤村レイコ（高坂保奈美、高坂ますみ）','篠田ゆう','羽生ありさ','若菜奈央','蓮実クレア',
             '跡美しゅり','通野未帆','風間ゆみ','麻里梨夏'}
    if i_dir in h_map:
        return True
    else:
        return False

#/cn/actresses/page/2
if __name__ == '__main__':
    i = 7
    while i < 10000:
        url = "https://avmoo.asia/cn/actresses/page/"+str(i)
        print("开始解析：" + url)
        if 1 == i:
            refer = 'https://avmoo.asia/cn/actresses/2'
        else:
            refer = 'https://avmoo.asia/cn/actresses/'+str(i-1)
        i = i + 1
        # 女星姓名 + 跳转链接的map表
        img_dirs = get_current_thumbs_list(url, refer)
        if None == img_dirs:
            print("无法获取该网页下的相册内容...")
            break
        else:
            for d in img_dirs:
                if consume_last(d):
                    continue
                # print(img_dirs.get(d))
                url_parser = img_dirs.get(d)
                # 爬取女星的资料
                # download_imgs((d, url_parser, refer, [1, url_parser]))
                my_thread = MyThread(download_imgs, (d, url_parser, refer, [1, url_parser]))
                my_thread.start()
                my_thread.join()
        print("[Main], "+str(i))