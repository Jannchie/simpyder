# coding=utf-8
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


class Spider():

  def gen_url(self):
    self.except_queue.put('未实现方法: gen_url()，无法开启爬虫任务。')
    yield None

  def get_response(self, url):
    return self.get(url)

  def parse(self, response):
    self.logger.critical('未实现方法: parse(response)，将直接返回Response对象')
    return response

  def save(self, item):
    self.logger.critical('未实现方法: save(item)，将直接打印爬取内容。')
    print(item)
    return item

  def __run_save(self):
    logger = _get_logger(f"{self.name} - 子线程 - SAVE", self.config.LOG_LEVEL)
    count = 0
    while True:
      if not self.item_queue.empty():
        count = 0
        self._saving = True
        try:
          item = self.item_queue.get()
          if item is None or item == False:
            continue
          logger.debug(item)
          item = self.save(item)
          self.meta['item_count'] += 1
          if self._finish == True:
            return
        except Exception as e:
          self.logger.exception(e)
      else:
        self._saving = False
        sleep(1)

  def assemble(self, gen_url=None, parse=None, save=None, config: SimpyderConfig = SimpyderConfig()):
    if gen_url != None:
      self.gen_url = gen_url
    if parse != None:
      self.parse = parse
    if save != None:
      self.save = save
    self.set_config(config)

  def set_config(self, config: SimpyderConfig):
    self.config = config

  def __apply_config(self):
    if self.config.HEADERS is None:
      self.headers = {'cookie': self.config.COOKIE,
                      'User-Agent': self.config.USER_AGENT}
    else:
      self.headers = self.config.HEADERS
    self.PARSE_THREAD_NUMER = self.config.PARSE_THREAD_NUMER
    if (len(self.config.USER_AGENT) < 30):
      self.logger.critical(f"使用User-Agent：{self.config.USER_AGENT}")
    else:
      self.logger.critical(f"使用User-Agent：{self.config.USER_AGENT[:30]}...")
    self.logger.critical(f"使用COOKIE：{self.config.COOKIE}")
    self.logger.critical(f"线程数：{self.config.PARSE_THREAD_NUMER}")

  def get(self, url):
    response = self.session.get(url, headers=self.headers)
    if 'html' in response.headers['content-type']:
      response.xpath = HTML(response.text).xpath
    return response

  def __init__(self, name="Simpyder", gen_url=None, parse=None, save=None, config=SimpyderConfig()):
    # 配置Session，复用TCP连接
    self.session = requests.session()
    self.session.mount('http://', HTTPAdapter(max_retries=3))
    self.session.mount('https://', HTTPAdapter(max_retries=3))

    # 载入配置
    self.config = config

    # 载入主线程日志记录
    self.logger = _get_logger(f"{name} - 主线程", self.config.LOG_LEVEL)

    # 构造函数组装
    self.assemble(gen_url, parse, save)

    self.QUEUE_LEN = self.config.PARSE_THREAD_NUMER * 2
    self.url_queue = queue.Queue(self.QUEUE_LEN)
    self.item_queue = queue.Queue(self.QUEUE_LEN)
    self.except_queue = queue.Queue(1)
    self.queueLock = threading.Lock()
    self.threads = []
    self.name = name
    self._saving = True

  def __get_info(self):
    log = _get_logger(f"{self.name} - 子线程 - INFO", self.config.LOG_LEVEL)
    history = []
    interval = 5
    while True:
      c_time = datetime.datetime.now()
      history.append(
          (c_time, self.meta['link_count'], self.meta['item_count']))
      if len(history) > 60:
        history = history[-60:]
      if (c_time - self.meta['start_time']).total_seconds() % interval < 1 and len(history) > 1:
        delta_link = (history[-interval + 1][1] - history[0][1]) * 60 / \
              ((history[-interval + 1][0] - history[0][0]).total_seconds() + 1)
        delta_item = (history[-interval + 1][2] - history[0][2]) * 60 / \
              ((history[-interval + 1][0] - history[0][0]).total_seconds() + 1)
        if (self.config.DOWNLOAD_INTERVAL == 0):
          load = 100
        else:
          load = int((history[-1][1] - history[0][1]) * 60 /
                     (history[-1][0] - history[0][0]).total_seconds() /
                     (60 / (self.config.DOWNLOAD_INTERVAL / self.config.PARSE_THREAD_NUMER)) * 100)
        result = {
            'computer_name': socket.gethostname(),
            'spider_name': self.start_time,
            'start_time': self.start_time,
            'update_time': datetime.datetime.now(),
            'load': load,
            'delta_link': delta_link,
            'delta_item': delta_item
        },
        log.info(
            f"正在爬取第 {self.meta['link_count']} 个链接({int(delta_link)}/min, 负载{load}%),共产生 {self.meta['item_count']} 个对象({int(delta_item)}/min)"
        )
      sleep(1)

  def run(self):
    self.start_time = datetime.datetime.now()
    self._finish = False
    print("""
       _____ _  Author: Jannchie         __         
      / ___/(_)___ ___  ____  __  ______/ /__  _____
      \__ \/ / __ `__ \/ __ \/ / / / __  / _ \/ ___/
     ___/ / / / / / / / /_/ / /_/ / /_/ /  __/ /    
    /____/_/_/ /_/ /_/ .___/\__, /\__,_/\___/_/     
                    /_/    /____/   version: {}      


        """ .format(__VERSION__))
    self.__apply_config()

    self.logger.critical(f"Simpyder ver.{__VERSION__}")
    self.logger.critical("启动爬虫任务")
    meta = {
        'link_count': 0,
        'item_count': 0,
        'thread_number': self.config.PARSE_THREAD_NUMER,
        'download_interval': self.config.DOWNLOAD_INTERVAL,
        'start_time': self.start_time,
    }
    self.meta = meta
    info_thread = threading.Thread(target=self.__get_info, name="状态打印线程")
    info_thread.setDaemon(True)
    info_thread.start()
    save_thread = threading.Thread(target=self.__run_save, name="保存项目线程")
    save_thread.setDaemon(True)
    save_thread.start()
    for i in range(self.PARSE_THREAD_NUMER):
      self.threads.append(
          self.ParseThread(
              f'{self.name} - 子线程 - No.{i}',
              self.url_queue,
              self.queueLock,
              self.get_response,
              self.parse,
              self.save,
              self.except_queue,
              self.item_queue,
              meta,
              self.config,
          ))
    for each_thread in self.threads:
      each_thread.setDaemon(True)
      each_thread.start()
    url_gener = self.gen_url()
    for each_url in url_gener:
      self.queueLock.acquire()
      while (self.url_queue.full()):
        if self.queueLock.locked():
          self.logger.debug(f"队列满: {each_url}")
          self.queueLock.release()
        sleep(0.1)
      self.logger.debug(f"加入待爬: {each_url}")
      if self.queueLock.locked():
        self.queueLock.release()

      self.queueLock.acquire()
      self.url_queue.put(each_url)
      self.queueLock.release()

    self.logger.info("全部请求完毕，等待解析进程")
    while self.url_queue.empty() == False or self.item_queue.empty() == False or self._saving == True:
      if self.except_queue.empty() == False:
        except_info = self.except_queue.get()
        self.logger = _get_logger(self.name, self.config.LOG_LEVEL)
        self.logger.error(except_info)
        # for each_thread in self.threads:
        #     each_thread.join()
        break
    self.logger.critical("全部解析完毕,等待保存进程")
    self._finish = True
    save_thread.join()
    self.logger.critical(f'合计爬取项目数：{meta["item_count"]}')
    self.logger.critical(f'合计爬取链接数：{meta["link_count"]}')

  class ParseThread(threading.Thread):
    def __init__(self, name, url_queue, queueLock, get_response, parse, save, except_queue, item_queue, meta, config):
      threading.Thread.__init__(self, target=self.run)
      self.name = name
      self.url_queue = url_queue
      self.queueLock = queueLock
      self.get_response = get_response
      self.parse = parse
      self.save = save
      self.item_queue = item_queue
      self.except_queue = except_queue
      self.logger = _get_logger(self.name, config.LOG_LEVEL)
      self.meta = meta

    def run(self):
      while True:
        try:
          sleep(self.meta['download_interval'])
          self.queueLock.acquire()
          if not self.url_queue.empty():
            url = self.url_queue.get()
            self.meta['link_count'] += 1
          else:
            url = None
          self.queueLock.release()

          if url is None:
            sleep(1)
            continue
          self.logger.debug(f"开始爬取 {url}")
          response = self.get_response(url)
          try:
            item = self.parse(response)
          except Exception as e:
            # 如果解析失败
            self.logger.exception(e)
            continue
          self.item_queue.put(item)
          datetime.timedelta(1)
        except NotImplementedError as e:
          self.logger.exception(e)
          return
        except Exception as e:
          self.logger.exception(e)
