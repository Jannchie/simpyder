# coding=utf-8

from simpyder import Spider


def gen_url():
    for each_id in range(100):
        yield "https://www.bilibili.com/video/av{}".format(each_id)


def parse(response):
    return response.xpath('//meta[@name="title"]/@content')[0]


def save(item):
    # print(item)
    pass


s1 = Spider(gen_url, parse, save, name="DEMO")
s1.run()

# s2 = Spider(name="DEMO")
# s2.assemble(gen_url, parse, save)
# s2.run()
