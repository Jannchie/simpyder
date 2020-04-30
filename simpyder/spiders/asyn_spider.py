# coding=utf-8
import asyncio
from time import sleep
import threading
import queue
import logging
import requests
from requests.adapters import HTTPAdapter
from lxml.etree import HTML
import datetime

import socket
from simpyder.config import SimpyderConfig

from simpyder.utils import _get_logger
from simpyder.__version__ import __VERSION__


class AsynSpider():
  async def get(self, url):
    response = self.session.get(url, headers=self.headers)
    if 'html' in response.headers['content-type']:
      response.xpath = HTML(response.text).xpath
    return response

  def gen_url(self):
    self.except_queue.put('未实现方法: gen_url()，无法开启爬虫任务。')
    yield None

  async def parse(self, response):
    self.logger.critical('未实现方法: parse(response)，将直接返回Response对象')
    return response

  async def save(self, item):
    self.logger.critical('未实现方法: save(item)，将直接打印爬取内容。')
    print(item)
    return item

  def __init__(self, name="Simpyder", user_agent="Simpyder ver.{}".format(__VERSION__), interval=0, concurrency=8):
    self.log_interval = 5

    self.name = name
    self.user_agent = user_agent
    self.concurrency = concurrency
    self.interval = interval

    self._url_count = 0
    self._item_count = 0
    self._statistic = []

    self.session = requests.session()
    self.session.mount('http://', HTTPAdapter(max_retries=3))
    self.session.mount('https://', HTTPAdapter(max_retries=3))

  def run(self):
    self.headers = {
        'user-agent': self.user_agent
    }
    self.logger = _get_logger("{}".format(self.name), "INFO")
    print("""\033[0;32m
   _____ _  Author: Jannchie         __
  / ___/(_)___ ___  ____  __  ______/ /__  _____
  \__ \/ / __ `__ \/ __ \/ / / / __  / _ \/ ___/
 ___/ / / / / / / / /_/ / /_/ / /_/ /  __/ /
/____/_/_/ /_/ /_/ .___/\__, /\__,_/\___/_/
                /_/    /____/  version: {}\033[0m """ .format(__VERSION__))
    self.logger.critical("user_agent: %s" % self.user_agent)
    self.logger.critical("concurrency: %s" % self.concurrency)
    self.logger.critical("interval: %s" % self.interval)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._run())
    loop.close()

  def _print_log(self):

    self._statistic.append({
        'url_count': self._url_count,
        'item_count': self._item_count,
        'time': datetime.datetime.now()
    })
    if (len(self._statistic) > 10):
      self._statistic = self._statistic[1:10]
    delta_url_count = self._statistic[-1]['url_count'] - \
        self._statistic[0]['url_count']
    delta_item_count = self._statistic[-1]['item_count'] - \
        self._statistic[0]['item_count']
    delta_seconds = (self._statistic[-1]['time'] -
                     self._statistic[0]['time']).seconds
    url_rate = 0 if delta_seconds == 0 else delta_url_count / \
        (delta_seconds / 60)
    item_rate = 0 if delta_seconds == 0 else delta_item_count / \
        (delta_seconds / 60)

    loading = "[限速基线：{}%]".format(
        int(url_rate / (60 / self.interval) * 100)) if self.interval != 0 else ""

    self.logger.info("已经爬取{}个链接({}/min)，共产生{}个对象({}/min) {}"
                     .format(self._url_count,
                             int(url_rate),
                             self._item_count, int(item_rate), loading))

  async def _auto_print_log(self):
    self._last_url_count = 0
    self._last_item_count = 0
    while True:
      await asyncio.sleep(self.log_interval)
      self._print_log()

  async def _run(self):
    self.logger.critical("Spider Task Start")
    start_time = datetime.datetime.now()
    url_gener = self.gen_url()
    tasks = []
    asyncio.create_task(self._auto_print_log())
    # 并发队列
    url_queue = queue.Queue(self.concurrency)
    for url in url_gener:
      url_queue.put(asyncio.create_task(self.crawl_one_url(url)))
      # 队列满则并发发起请求
      if url_queue.full():
        while False == url_queue.empty():
          await asyncio.sleep(self.interval)
          await url_queue.get()
    while False == url_queue.empty():
      await asyncio.sleep(self.interval)
      await url_queue.get()
    self._print_log()
    self.logger.critical("Simpyder任务执行完毕")
    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    self.logger.critical('累计消耗时间：% s' % str(delta_time))

  async def crawl_one_url(self, url):
    res = await self.get(url)
    self._url_count += 1
    item = await self.parse(res)
    count = await self.save(item)
    if type(count) == int:
      self._item_count += count
    else:
      self._item_count += 1


if __name__ == "__main__":
  s = AsynSpider()

  def g():
    count = 0
    while count < 800:
      if count % 100 == 0:
        sleep(0.001)
      count += 1
      yield "http://www.baidu.com"
  s.gen_url = g

  async def parse(res):
    return "parsed item"
  s.parse = parse

  async def save(item):
    return 2
  s.save = save
  s.run()
