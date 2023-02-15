# coding=utf-8
'''
这是一个DEMO。该程序用于爬取B站AV号小于100的视频页面标题
'''

import requests
from simpyder import Spider
from simpyder import SimpyderConfig


def gen_url():
  for each_id in range(100):
    yield f"https://www.bilibili.com/video/av{each_id}"


def parse(response):
  return response.xpath('//meta[@name="title"]/@content')[0]


def save(item):
  print(item)


if __name__ == "__main__":
  s1 = Spider("BILIBILI TITLE SPIDER", gen_url, parse, save)
  sc = SimpyderConfig()
  sc.COOKIES = "example:value;"
  sc.USER_AGENT = "my user agent"
  s1.assemble(gen_url=gen_url, parse=parse, save=save, config=sc)
  s1.run()
