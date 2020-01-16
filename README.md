# Spipy - 轻量级多线程爬虫

最简爬虫实践

## 特点

- 分布式
- 通用化
- 多线程
  
## 使用说明

用户只需要实现三个方法：

### 链接获取方法

``` python
def gen_url():
    for each_id in range(100):
        yield "https://www.biliob.com/api/video/{}".format(each_id)
```

### 链接解析方法

``` python
def parse(response, key=None):
    return response.xpath('//meta[@name="title"]/@content')[0]
```

### 数据导出方法

``` python
def save(item):
    print(item)
```

### 然后将这些模块组成一个Spider

``` python
s = Spider(gen_url, parse, save, name="DEMO") # 构造函数方式组装
# Or
s = Spider()
s.assemble(gen_url, parse, save, name="DEMO") # 先创建爬虫对象，再装载各个模块
```

### 接着就可以开始爬虫任务

``` python
s.run()
```
