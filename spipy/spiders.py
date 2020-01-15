from time import sleep
import threading
import queue
import logging
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s @ %(name)s: %(message)s')


class Spider():

    class ParseThread(threading.Thread):
        def __init__(self, name, queue, queueLock, get_response, parse, save):
            threading.Thread.__init__(self)

            self.name = name
            self.queue = queue
            self.queueLock = queueLock
            self.get_response = get_response
            self.parse = parse
            self.save = save

        def get_key(self):
            self.queueLock.acquire()
            if not self.queue.empty():
                key = self.queue.get()
            else:
                key = None
            self.queueLock.release()
            return key

        def run(self):
            while True:
                try:
                    key = self.get_key()
                    if key == None:
                        sleep(1)
                        continue

                    response = self.get_response(key)
                    item = self.parse(response, key)
                    self.save(item)
                except Exception as error:
                    # 出现错误时打印错误日志
                    logging.error("SAVE ERROR")
                    print(error)

    def get_key(self):
        raise NotImplementedError

    def get_response(self, key):
        raise NotImplementedError

    def parse(self, response, key=None):
        raise NotImplementedError

    def save(self, item):
        raise NotImplementedError

    def __init__(self):
        self.NAME = "Spider"
        self.QUEUE_LEN = 1000
        self.PARSE_THREAD_NUMER = 8
        self.item_queue = queue.Queue(self.QUEUE_LEN)
        self.queueLock = threading.Lock()
        for i in range(self.PARSE_THREAD_NUMER):
            self.ParseThread(self.NAME, self.item_queue, self.queueLock,
                             self.get_response, self.parse, self.save).start()
        self.get_key()
