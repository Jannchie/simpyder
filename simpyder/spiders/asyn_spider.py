# coding=utf-8
import asyncio
from time import sleep
import threading
from asyncio.queues import Queue
import logging
import requests
from requests.adapters import HTTPAdapter
from lxml.etree import HTML
import datetime
import aiohttp
import socket
from simpyder.config import SimpyderConfig

from asyncio import TimeoutError

from simpyder.utils import _get_logger
from simpyder.__version__ import __VERSION__


class AsynSpider():
  async def gen_proxy(self):
    while True:
      yield ""

  async def __update_proxy(self):
    if len(self.succeed_proxies) != 0:
      self.proxy = next(iter(self.succeed_proxies))
    else:
      self.proxy = await self.proxy_gener.__anext__()

  async def get(self, url, proxy='', retry=5):
    response = None
    # 重试次数
    for i in range(retry):
      try:
        response = await self.session.get(
            url, headers=self.headers, proxy='' if proxy == None else proxy, timeout=5)
        if 'content-type' in response.headers and 'html' in response.content_type:
          response.xpath = HTML(await response.text()).xpathW
        if response.content_type == 'application/json':
          response.json_data = await response.json()
        if response.status != 200 or self.except_content_type != None and response.content_type != self.except_content_type:
          if proxy != None:
            await self.__update_proxy()
            proxy = self.proxy
          continue
        break
      except (Exception, BaseException, TimeoutError) as e:
        if proxy != None:
          await self.__update_proxy()
          proxy = self.proxy
        continue
      break
    if response != None and response.status == 200:
      self.succeed_proxies.add(proxy)
    else:
      self.succeed_proxies.discard(self.proxy)
      if proxy != None:
        await self.__update_proxy()
    return response

  async def gen_url(self):
    self.except_queue.put('未实现方法: gen_url()，无法开启爬虫任务。')
    yield None

  async def parse(self, response):
    self.logger.critical('未实现方法: parse(response)，将直接返回Response对象')
    return response

  async def save(self, item):
    self.logger.critical('未实现方法: save(item)，将直接打印爬取内容。')
    print(item)
    return item

  def __init__(self, name="Simpyder", user_agent="Simpyder ver.{}".format(__VERSION__), interval=0, concurrency=8, log_level='INFO'):
    self.count = 0
    self.finished = False
    self.log_interval = 5
    self.name = name
    self.succeed_proxies = set()
    self.retry = 5
    self.user_agent = user_agent
    self.concurrency = concurrency
    self.interval = interval
    self.log_level = log_level
    self.proxy = ''
    self._url_count = 0
    self._item_count = 0
    self._statistic = []
    self.except_content_type = None
    self.headers = {
        'user-agent': self.user_agent
    }
    # self.session = requests.session()
    # self.session.mount('http://', HTTPAdapter(max_retries=3))
    # self.session.mount('https://', HTTPAdapter(max_retries=3))
    self.session = aiohttp.ClientSession()

  def run(self):
    self.logger = _get_logger("{}".format(self.name), self.log_level)
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
    self.proxy_gener = self.gen_proxy()
    self.loop = asyncio.get_event_loop()
    self.loop.run_until_complete(self._run())
    self.loop.close()

  async def _print_log(self):
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
    while self.finished == False:
      await self._print_log()
      await asyncio.sleep(self.log_interval)

  async def crawl_one_url(self, url, proxy):
    try:
      self.logger.debug(f"> Crawl a Url: {url}")
      if type(url) == str and url[0:4] == 'http':
        self.logger.debug(f"下载数据：{url}")
        res = await self.get(url, proxy)
        if res == None:
          self.logger.warning(f"下载数据失败 {url} {proxy}")
      else:
        self.logger.debug(f"非URL直接返回")
        res = url
      self._url_count += 1
      item = await self.parse(res)
      count = await self.save(item)
      if type(count) == int:
        self._item_count += count
      else:
        self._item_count += 1
      self.logger.debug(f"√ Crawl a Url: {url}")
    except Exception as e:
      self.logger.exception(e)

  async def __crawl(self, crawl_sem, lock):
    async with crawl_sem:
      try:
        if not self.url_task_queue.empty():
          await lock.acquire()
          self.count += 1
          try:
            lock.release()
            url = await self.url_task_queue.get()
            await self.crawl_one_url(url, self.proxy)
            url = self.url_task_queue.task_done()
          finally:
            await lock.acquire()
            self.count -= 1
            lock.release()
        else:
          await asyncio.sleep(0)
      except Exception as e:
        self.logger.exception(e)

  async def _run_crawler(self, i):
    try:
      crawl_sem = asyncio.Semaphore(self.concurrency)
      lock = asyncio.Lock()
      self.logger.info(f"Start Crawler: {i}")
      while self.finished == False or not self.url_task_queue.empty():
        await asyncio.sleep(0)
        async with crawl_sem:
          asyncio.ensure_future(self.__crawl(crawl_sem, lock))
    except Exception as e:
      self.logger.exception(e)

  async def _add_url_to_queue(self):
    url_gener = self.gen_url()
    async for url in url_gener:
      await asyncio.sleep(self.interval)
      self.logger.debug(f"Crawl Url: {url}")
      await self.url_task_queue.put(url)

  async def _run(self):
    self.logger.debug("Spider Task Start")

    self.proxy = await self.proxy_gener.__anext__()

    self.url_task_queue = Queue(30)

    start_time = datetime.datetime.now()
    tasks = []

    print_log = asyncio.ensure_future(self._auto_print_log())

    self.logger.debug("Create Crawl Tasks")

    crawl_task = asyncio.ensure_future(self._run_crawler(0))

    await self._add_url_to_queue()
    await asyncio.sleep(5)
    while not self.url_task_queue.empty() or self.count != 0:
      await asyncio.sleep(5)
    self.finished = True
    await crawl_task
    self.logger.critical("Simpyder任务执行完毕")
    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    self.logger.critical('累计消耗时间：% s' % str(delta_time))
    self.logger.critical('累计爬取链接：% s' % str(self._url_count))
    self.logger.critical('累计生成对象：% s' % str(self._item_count))

    await print_log
    await self.session.close()


if __name__ == "__main__":
  s = AsynSpider()
  s.concurrency = 64
  s.interval = 0

  async def g():
    count = 0
    while count < 1024:
      count += 1
      # await asyncio.sleep(0.1)
      yield "https://www.baidu.com"
  s.gen_url = g

  async def parse(res):
    await asyncio.sleep(0.1)
    return "parsed item"
  s.parse = parse

  async def save(item):
    await asyncio.sleep(0.1)
    return 2
  s.save = save
  s.run()
