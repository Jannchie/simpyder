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

我们需要一个定义一个[生成器](https://docs.python.org/zh-cn/3/c-api/gen.html)，用于产生链接。

``` python
def gen_url():
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

参见[B站视频标题爬虫](./demo/demo.py)

---

- 该项目由[@Jannchie](https://github.com/Jannchie)维护
- 你可以通过邮箱[jannchie@gmail.com](jannchie@gmail.com)进行联系
