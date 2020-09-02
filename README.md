# Simpyder - Simple Python Spider

Simpyder - 轻量级**协程**Python爬虫

## 特点

- 轻量级：下载便利，依赖较少，使用简单。
- 协程：单线程，通过协程实现并发。
- 可定制：简单配置，适应各种爬取场合。
  
## 快速开始

### 下载

```bash
#使用pip3
pip3 install simpyder --user
```

```bash
# 更新包
pip3 install simpyder --upgrade
```

### 编码

用户只需要定义三个函数，实现三个模块：

#### 链接获取

我们需要一个定义一个[异步生成器](https://docs.python.org/zh-cn/3/c-api/gen.html)，用于产生链接。

``` python
async def gen_url():
    for each_id in range(100):
        yield "https://www.biliob.com/api/video/{}".format(each_id)
```

#### 链接解析

我们需要定义一个解析链接的函数。其中第一个参数是Response对象，也就是上述函数对应URL的访问结果。

该函数需要返回一个对象，作为处理结果。

注意，与普通函数不同，这是一个协程函数。需要在前面加上`async`。代表该函数是异步的。

``` python
async def parse(response):
    return response.xpath('//meta[@name="title"]/@content')[0]
```

#### 数据导出

上面函数的处理结果将在这个函数中统一被导出。下列例子为直接在控制台中打印导出结果。

保存需要IO操作，因此这个函数可能运行较慢，因此也需要是异步的。我们在前面添加`async`关键词

``` python
async def save(item):
    print(item)
```

### 然后将这些模块组成一个Spider

首先导入爬虫对象:

``` python
import AsynSpider from simpyder.spiders
```

你可以这样组装Spider

``` python
spider = AsyncSpider()
spider.gen_url = gen_url
spider.parse = parse
spider.save = save
```

### 接着就可以开始爬虫任务

``` python
s.run()
```

### 你也可以通过构造函数进行一些配置

``` python

spider = AsyncSpider(name="TEST")
```

## 示例程序

``` python
from simpyder.spiders import AsynSpider

# new一个异步爬虫
s = AsynSpider()

# 定义链接生成的生成器，这里是爬取800次百度首页的爬虫
def g():
  count = 0
  while count < 800:
    count += 1
    yield "https://www.baidu.com"

# 绑定生成器
s.gen_url = g

# 定义用于解析的异步函数，这里不进行任何操作，返回一段文本
async def p(res):
  return "parsed item"

# 绑定解析器
s.parse = p

# 定义用于存储的异步函数，这里不进行任何操作，但是返回2，表示解析出2个对象
async def s(item):
  return 2

# 绑定存储器
s.save = s

# 运行
s.run()

```

## 理论速率

运行上述代码，可以得到单进程、并发数：64、仅进行计数操作的下载速率：

``` log
[2020-09-02 23:42:48,097][CRITICAL] @ Simpyder: user_agent: Simpyder ver.0.1.9
[2020-09-02 23:42:48,169][CRITICAL] @ Simpyder: concurrency: 64
[2020-09-02 23:42:48,244][CRITICAL] @ Simpyder: interval: 0
[2020-09-02 23:42:48,313][INFO] @ Simpyder: 已经爬取0个链接(0/min)，共产生0个对象(0/min) 
[2020-09-02 23:42:48,319][INFO] @ Simpyder: Start Crawler: 0
[2020-09-02 23:42:53,325][INFO] @ Simpyder: 已经爬取361个链接(4332/min)，共产生658个对象(7896/min) 
[2020-09-02 23:42:58,304][INFO] @ Simpyder: 已经爬取792个链接(5280/min)，共产生1540个对象(10266/min) 
[2020-09-02 23:43:03,304][INFO] @ Simpyder: 已经爬取1024个链接(4388/min)，共产生2048个对象(8777/min) 
[2020-09-02 23:43:05,007][CRITICAL] @ Simpyder: Simpyder任务执行完毕
[2020-09-02 23:43:05,008][CRITICAL] @ Simpyder: 累计消耗时间：0:00:16.695013
[2020-09-02 23:43:05,008][CRITICAL] @ Simpyder: 累计爬取链接：1024
[2020-09-02 23:43:05,009][CRITICAL] @ Simpyder: 累计生成对象：2048
```

---

- 该项目由[@Jannchie](https://github.com/Jannchie)维护
- 你可以通过邮箱[jannchie@gmail.com](jannchie@gmail.com)进行联系