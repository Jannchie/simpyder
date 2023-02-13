import csv
from csv import DictReader
from time import sleep
from simpyder import Spider
from simpyder import FAKE_UA
from simpyder import SimpyderConfig
import simpyder
import re
import datetime

from pymongo import MongoClient
import os
env_dist = os.environ
# 存入mongodb
client = MongoClient(env_dist.get("BILIOB_MONGO_URL"))
db = client.zhihu

# 该网站的爬取需要伪造cookies，请填入自己的cookie
cookie = ''


def get_url():
  while True:
    yield 'https://www.zhihu.com/hot'
    sleep(60)


def parse(response):
  hot_list = response.xpath('//div[@class="HotItem-content"]')
  data = []
  for hot_item in hot_list:
    try:
      title = hot_item.xpath('.//h2[@class="HotItem-title"]/text()')[0]
      print(title)
      point = re.findall(r"\d+\.?\d*", hot_item.xpath(
          './/div[contains(@class,"HotItem-metrics")]/text()')[0])[0]

      print(point)
      data.append({
          'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
          'title': title,
          'value': int(point)
      })
    except Exception as e:
      print('[ERROR]'.format(title))
  return data


f = csv.DictWriter(open('./zhihu.csv', 'w', encoding='utf-8-sig'),
                   fieldnames=['date', 'title', 'value'])


def save(items):
  for item in items:
    f.writerow(item)


s = Spider()
s.assemble(get_url, parse, save)

sc = SimpyderConfig()
sc.PARSE_THREAD_NUMER = 1
sc.COOKIE = cookie
sc.USER_AGENT = FAKE_UA
s.set_config(sc)
s.run()
