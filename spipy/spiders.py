from time import sleep
import threading
import queue
import logging
import requests
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}


def get_logger(name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s @ %(name)s: %(message)s'))
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.critical("启动线程 {}".format(name))
    return logger


class Spider():

    def gen_url(self):
        self.except_queue.put('未实现方法: gen_url()')
        yield None

    def get_response(self, url):
        response = requests.get(url, headers=headers)
        return response

    def parse(self, response, key=None):
        self.except_queue.put('未实现方法: parse(response, key)')
        return None

    def save(self, item):
        self.except_queue.put('未实现方法: save(item)')
        return None

    def assemble(self, gen_url=None, parse=None, save=None):
        if gen_url != None:
            self.gen_url = gen_url
        if parse != None:
            self.parse = parse
        if save != None:
            self.save = save
        pass

    def __init__(self, gen_url=None, parse=None, save=None):
        self.assemble(gen_url, parse, save)
        self.QUEUE_LEN = 1000
        self.NAME = "NAMELESS"
        self.PARSE_THREAD_NUMER = 8
        self.item_queue = queue.Queue(self.QUEUE_LEN)
        self.except_queue = queue.Queue(1)
        self.queueLock = threading.Lock()
        self.threads = []

    def run(self):
        for i in range(self.PARSE_THREAD_NUMER):
            self.threads.append(self.ParseThread(self.NAME + ' ' + str(i), self.item_queue, self.queueLock,
                                                 self.get_response, self.parse, self.save, self.except_queue))
        for each_thread in self.threads:
            each_thread.setDaemon(True)
            each_thread.start()
        url_gener = self.gen_url()
        for each_url in url_gener:
            self.queueLock.acquire()
            self.item_queue.put(each_url)
            self.queueLock.release()
        while (True):
            sleep(1)
            except_info = self.except_queue.get()
            if except_info != None:
                self.logger = get_logger(self.NAME)
                self.logger.error(except_info)
                # for each_thread in self.threads:
                #     each_thread.join()
                break

    class ParseThread(threading.Thread):
        def __init__(self, name, item_queue, queueLock, get_response, parse, save, except_queue):
            threading.Thread.__init__(self, target=self.run)
            self.name = name
            self.item_queue = item_queue
            self.queueLock = queueLock
            self.get_response = get_response
            self.parse = parse
            self.save = save
            self.except_queue = except_queue
            self.logger = get_logger(self.name)

        def run(self):
            try:
                while True:
                    self.queueLock.acquire()
                    if not self.item_queue.empty():
                        url = self.item_queue.get()
                    else:
                        url = None
                    self.queueLock.release()
                    if url == None:
                        sleep(1)
                        continue
                    self.logger.debug("开始爬取 {}".format(url))

                    response = self.get_response(url)
                    item = self.parse(response, url)
                    self.logger.debug(item)
                    self.save(item)
            except NotImplementedError as e:
                pass
            except Exception as e:
                self.logger.error(e)
