from spipy import Spider
import requests
from lxml.etree import HTML


# class Demo(Spider):
#     def __init__(self):
#         super().__init__()
#         self.NAME = "demo"
#     pass

#     def gen_url(self):
#         for each_id in range(100):
#             yield "https://www.bilibili.com/video/av{}".format(each_id)

#     def parse(self, response, key=None):
#         return response

#     def save(self, item):
#         pass
#         print(HTML(item.text).xpath('//meta[@name="title"]/@content')[0])


def gen_url():
    for each_id in range(100):
        yield "https://www.bilibili.com/video/av{}".format(each_id)


def parse(response, key=None):
    return response


def save(item):
    pass
    print(HTML(item.text).xpath('//meta[@name="title"]/@content')[0])


# s = Spider()
s = Spider(gen_url, parse, save)
# s.assemble(gen_url, parse, save)
s.run()

# Demo()
