# Simpyder - **Si**mple **M**ultithreaded **Py**thon Spi**der**

Simpyder - 轻量级多线程Python爬虫

## 特点

- 轻量级：下载便利，使用简单。
- 多线程：并行下载解析，快速获取数据。
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

``` python
def parse(response):
    return response.xpath('//meta[@name="title"]/@content')[0]
```

#### 数据导出

上面函数的处理结果将在这个函数中统一被导出。下列例子为直接在控制台中打印导出结果。

``` python
def save(item):
    print(item)
```

### 然后将这些模块组成一个Spider

首先导入爬虫对象:

``` python
import Spider from simpyder
```

你可以使用构造函数组装Spider

``` python
s = Spider(gen_url, parse, save, name="DEMO") # 构造函数方式组装
```

也可以使用`assemble`函数进行组装

``` python

s = Spider()
s.assemble(gen_url, parse, save, name="DEMO") # 先创建爬虫对象，再装载各个模块
```

### 接着就可以开始爬虫任务

``` python
s.run()
```

### 你也可以配置进行一些简单的配置

``` python
from simpyder import SimpyderConfig
sc = SimpyderConfig
sc.COOKIES = "example:value"
sc.USER_AGENT = "my user agent"
s.assemble(gen_url=gen_url, parse=parse, save=save, name="DEMO",config=sc)
```

## 示例程序

参见[B站视频标题爬虫](./demo/demo.py)

---

- 该项目由[@Jannchie](https://github.com/Jannchie)维护
- 你可以通过邮箱[jannchie@gmail.com](jannchie@gmail.com)进行联系
