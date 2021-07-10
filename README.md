# 对京东热门书籍的数据分析

## 项目目录介绍

* data：代码运行时需要的一些文件
* jd-html：将爬下来的页面保存在本地，便于后续使用
* picture：数据分析保存下的一些图
* store：爬取数据后写入csv文件的位置
* main_*：爬虫代码
* book.ipynb：数据分析代码

## 数据采集

数据才是核心，但是如何去采集数据呢？

我们给出的答案是爬虫。

当然，遇到的问题是很多的，如当频繁访问时，京东的服务器会把你的ip封掉，只能不断地换ip了，当然还有使用time.sleep。

我们的字段设计为：

| 字段               | 解释             |
| ------------------ | ---------------- |
| goodsID            | 商品ID           |
| name               | 书籍名称         |
| type               | 书籍类型         |
| author             | 书籍作者         |
| page_size          | 书籍页数         |
| origin_price       | 原始价格         |
| preferential_price | 京东优惠后的价格 |
| publisher          | 书籍出版社       |
| comments_count     | 评论数           |
| favorable_rate     | 好评率           |
| publish_time       | 出版时间         |

爬虫：

![image-20210710091450220](http://picture.nj-jay.com/image-20210710091450220.png)

为了能确保程序写入文件时不发生异常，我们首先将需要的页面保存到本地。

再次运行时就可以不经过网络，直接从本地页面爬取数据。

我们设计数据采集的思路为：

首先抓取每一页的商品列表。

列表页我们只需要获取商品的ID即可。

![image-20210710091907223](http://picture.nj-jay.com/image-20210710091907223.png)

拿到商品的ID之后，我们就可以跳转到商品的具体页面，获取我们需要的所有数据。

![image-20210710092112457](http://picture.nj-jay.com/image-20210710092112457.png)

我们根据每个字段封装了函数，每个函数的参数都是商品的ID。

```shell
# 数据写入列表中
shop_info = []
for i in range(1, 16, 2):
    shop_id = getIdByPageSize(i)
    for id in shop_id:
        print("正在写入", i, "页数据")
        print("商品id", id)
        shop_info.append(id)
        shop_info.append(getName(id))
        shop_info.append("编程")
        shop_info.append(getAuthor(id))
        shop_info.append(getBookPageSize(id))
        shop_info.append(getOriginPrice(id))
        shop_info.append(getPreferentialPrice(id))
        shop_info.append(getPublisher(id))
        shop_info.append(getCommentsCount(id))
        shop_info.append(getFavorableRate(id))
        shop_info.append(getPublishTime(id))
        # time.sleep(2)
```

```shell
# 写入csv文件
b = [shop_info[i:i + 11] for i in range(0, len(shop_info), 11)]
with open("jd-item-info-coding.csv", 'w+', encoding='utf-8') as fp:
    for value in b:
        fp.write('\n')
        fp.write(",".join(value))
```

## 数据预处理

爬取出来的数据并不完美，需要我们对数据进行一些处理，方便后续的分析。

* 剔除重复的数据并重排索引
* 将某些字段的unkown剔除
* 将好评率转换为float类型
* 对评论数中的"万"换成0000，将"+"换成空，并转成整形

## 对数据进行分析

* 统计各个出版社书种类的数目
* 统计各个出版社的平均好评率
* 统计出书籍好评率的分布
* 统计书籍价格在100元以上的在哪些出版社
* 不同类型书籍的评论数前十
* 不同类型书籍词云图分析

## 小组分工

| 小组成员 | 任务                               |
| -------- | ---------------------------------- |
| 聂健     | 负责爬取数据，后续项目规划，演讲   |
| 程欢     | 优化部分爬虫代码、数据分析，词云图 |
| 杜威威   | 数据整合以及ppt制作                |
| 桑梓     | 数据预处理与数据分析               |
| 徐旋泰   | 数据预处理以及数据分析             |
| 余烽     | 数据整合以及ppt制作                |
