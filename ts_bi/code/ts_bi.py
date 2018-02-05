#!/usr/bin/env python3.4
# encoding: utf-8
"""
Created on 18-2-2

@author: Xu
"""
import requests
import time
import pdfkit
import random

from lxml import etree
from bs4 import BeautifulSoup
from html_templates import html_template
from fake_useragent import UserAgent

ua = UserAgent()


def get_url():
    """
    获取博客地图所有文章列表链接
    :return:
    """
    map_url = 'https://ask.hellobi.com/blog/biwork/sitemap/'
    # map_url = 'https://ask.hellobi.com/blog/butaputong/sitemap/'
    map_headers = {
        "Host": "ask.hellobi.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ua.random,
    }
    rel = requests.get(url=map_url, headers=map_headers).content
    html = etree.HTML(rel)
    datas = html.xpath('//div[@class="col-md-12"]')
    list_url = []
    for data in datas[0]:
        blog_urls = data.xpath('./li/a/@href')
        if blog_urls:
            for blog_url in blog_urls:
                complete_url = 'https://ask.hellobi.com/' + blog_url
                list_url.append(complete_url)
    print(len(list_url))
    return list_url


def get_content(urls):
    """
    获取文章标题和正文
    :param urls:
    :return:
    """
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'outline-depth': 10,
    }
    htmls = []
    my_headers = {
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Host": "ask.hellobi.com",
        "User-Agent": ua.random
    }
    for index, url in enumerate(urls):
        result = requests.get(url=url, headers=my_headers).content
        soup = BeautifulSoup(result, 'html.parser')
        re_html = etree.HTML(result)
        user_name = re_html.xpath('/html/body/div[1]/aside/section/div[1]/div/a/text()')[0]
        datas = re_html.xpath('//div[@class="aw-mod aw-question-detail"]')
        title = datas[0].xpath('//h1/a/text()')[0]  # 获取文章标题
        # article = datas[0].xpath('//div[@class="message-content editor-style"]')[0].xpath('string()')  # 获取文章内容
        body = soup.find_all(class_='message-content')
        print(title, body)
        # 将标题加入正文居中
        center_title = soup.new_tag('center')
        title_tag = soup.new_tag('h1')
        title_tag.string = title
        center_title.insert(1, title_tag)
        html = str(body)
        print(html)
        html = html_template.format(content=html)
        html = html.encode("utf-8")
        f_name = ".".join([str(index), "html"])
        with open(f_name, 'wb') as f:
            f.write(html)
        htmls.append(f_name)
        time.sleep(2)
        try:
            pdfkit.from_file(htmls, user_name + "的文章合辑.pdf", options=options)  # 将html文件合并为pdf
        except Exception as e:
            print(e)


if __name__ == '__main__':
    content = get_url()
    get_content(content)
