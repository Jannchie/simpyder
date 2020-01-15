from pyspider import Spider
import requests
from lxml.etree import HTML
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}


class Demo(Spider):
    def __init__(self):
        super().__init__()
        self.NAME = "demo"
    pass

    def get_key(self):
        for each_id in range(100):
            self.item_queue.put(each_id)

    def get_response(self, key):
        response = requests.get(
            "https://www.bilibili.com/video/av{}".format(key), headers=headers)
        return response

    def parse(self, response, key=None):
        return response

    def save(self, item):
        print(HTML(item.text).xpath('//meta[@name="title"]/@content')[0])


Demo()
