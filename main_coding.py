# -*- coding:utf-8 -*-
import json
import requests
import os
from bs4 import BeautifulSoup
import time
import re
import codecs


# 根据pageSize获取每页60个书籍的id
def getIdByPageSize(pageSize):
    data_first = shopWebsiteFirst(pageSize)
    data_last = shopWebsiteLast(pageSize)
    shop_id = []
    for value in data_first:
        shop_id.append(value['data-sku'])
    for value in data_last:
        shop_id.append(value['data-sku'])
    return shop_id


# 根据id获取商品页面
def getItemInfoById(shopId):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64',
        'cookie': '3AB9D23F7A4B3C9B=D3OAJKRHRTXMRFJZFYLTOT3HKZVMQCMGKOMQAFBWIOW7YQBZF6JP2SVV5IO5XN2ITCHJAGBW2RZ4TYJFIPDHZGJUJ4',
        'refer': 'https://search.jd.com/'
    }
    url = 'https://item.jd.com/%s.html' % shopId
    res = requests.get(url=url, headers=headers)
    data = ''
    if os.path.exists('jd-html/item/coding/' + shopId + '.html'):
        print("read" + shopId + '.html')
        with codecs.open('jd-html/item/coding/' + shopId + '.html', 'r', encoding='utf-8') as fp:
            data = fp.read()
    else:
        data = res.content.decode('utf-8')
        with codecs.open('jd-html/item/coding/' + shopId + '.html', 'w', encoding='utf-8') as fp:
            fp.write(data)
    soup = BeautifulSoup(data, 'html.parser')
    item_info = soup.find('body')
    return item_info


# 根据id获取书籍名称
def getName(shopId):
    item_info = getItemInfoById(shopId)
    if item_info is None:
        return "unknown"
    name_sku = item_info.find('div', attrs={'class': 'sku-name'})
    if name_sku is None:
        return "unknown"
    name = name_sku.get_text().replace(" ", "", -1).replace(",", " ", -1).replace("，", " ", -1)
    return name.strip()


# 根据id获取书籍作者
def getAuthor(shopId):
    item_info = getItemInfoById(shopId)
    if item_info is None:
        return "unknown"

    author_p = item_info.find('div', attrs={'class': 'p-author'})
    if author_p is None:
        return "unknown"
    author = author_p.get_text()
    return author.strip().replace('，', " ", -1).replace(",", " ", -1)


def getBookCoverInfo(shopId):
    item_info = getItemInfoById(shopId)
    if item_info is None:
        return None
    book_cover_introduction = item_info.find('ul', attrs={'class': "parameter2 p-parameter-list"})
    if book_cover_introduction is None:
        return None
    return book_cover_introduction


# 根据id获取出版社
def getPublisher(shopId):
    # 书籍封面的一些信息 如出版社 ISBN号 版次 出版时间 字数  页数 包装等信息
    book_cover_introduction = getBookCoverInfo(shopId)
    if book_cover_introduction is None:
        return "unknown"
    publisher = book_cover_introduction.find('li', attrs={'clstag': 'shangpin|keycount|product|chubanshe_3'}).find('a')[
        'title']
    return publisher


# 根据id获取出版时间
def getPublishTime(shopId):
    book_cover_introduction = getBookCoverInfo(shopId)
    if book_cover_introduction is None:
        return None
    book_cover_list = book_cover_introduction.find_all('li')
    date_reg_exp = re.compile('\d{4}[-/]\d{2}[-/]\d{2}')
    matches_list_time = date_reg_exp.findall(str(book_cover_list))
    if len(matches_list_time) >= 1:
        return matches_list_time[0]
    return "unknown"


# 根据id获取书籍页数
def getBookPageSize(shopId):
    book_cover_introduction = getBookCoverInfo(shopId)
    if book_cover_introduction is None:
        return "unknown"
    book_cover_list = book_cover_introduction.find_all('li')
    page_size = getStrBtw(str(book_cover_list), '页数：', "</li>")
    if page_size == "unknown":
        return "unknown"
    return page_size


# 获取中间字符串，不包含startStr, endStr
def getMiddleStr(content, startStr, endStr):
    startIndex, endIndex = 0, 0
    try:
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
    except:
        return None
    else:
        return content[startIndex:endIndex]


def getStrBtw(s, f, b):
    par = s.partition(f)
    if (par[2].partition(b))[0][:] == "":
        return "unknown"
    return (par[2].partition(b))[0][:]


# 根据id获取书籍所有价格
def getPrice(shopId):
    priceApi = 'https://p.3.cn/prices/mgets?skuIds=J_%s'
    res = requests.get(priceApi % shopId).content
    # print(type(res))  bytes
    # bytes 转 dict
    price_dict = eval(getMiddleStr(str(res), "b'[", "]"))
    return price_dict


# 根据id获取原始价格
def getOriginPrice(shopId):
    price_dict = getPrice(shopId)
    return price_dict['m']


# 根据id获取优惠价格
def getPreferentialPrice(shopId):
    price_dict = getPrice(shopId)
    return price_dict['p']


# 获取关于评论的一些参数  返回json数据
def getCommentInfo(shopId):
    url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64',
        'cookie': '3AB9D23F7A4B3C9B=D3OAJKRHRTXMRFJZFYLTOT3HKZVMQCMGKOMQAFBWIOW7YQBZF6JP2SVV5IO5XN2ITCHJAGBW2RZ4TYJFIPDHZGJUJ4'}

    data = ""
    if os.path.exists('jd-html/commentInfo/coding/' + shopId + '.html'):
        print("read" + shopId + '.html')
        with codecs.open('jd-html/commentInfo/coding/' + shopId + '.html', 'r', encoding='utf-8') as fp:
            data = fp.read()
    else:
        try:
            res = requests.get(url=url.format(shopId), headers=headers)
            data = res.content.decode('gbk')
        except:
            print("解码失败")
        else:
            with codecs.open('jd-html/commentInfo/coding/' + shopId + '.html', 'w', encoding='utf-8') as fp:
                fp.write(data)
    if data == "":
        return None
    data = getMiddleStr(data, 'fetchJSON_comment98(', ');')
    json_data = json.loads(data)
    return json_data


# 根据id获取该书籍的具体评论
# @param: shopId 商品id
# @param: count 你要获取的评论条数(请填写10的倍数) default = 10
def getSpecificComment(shopId, count=10):
    shop_comments = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'
    }
    url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'
    for i in range(count // 10):
        url_page = url.format(shopId, i)
        res = requests.get(url=url_page, headers=headers)
        data = res.content.decode('gbk')
        data = getMiddleStr(data, 'fetchJSON_comment98(', ');')
        json_data = json.loads(data)
        for value in json_data['comments']:
            shop_comments.append(value['content'])
    return shop_comments


# 根据id获取评论数
def getCommentsCount(shopId):
    json_data = getCommentInfo(shopId)
    if json_data is None:
        return 'unknown'
    return json_data['productCommentSummary']['commentCountStr']


# 根据id获取商品好评率
def getFavorableRate(shopId):
    json_data = getCommentInfo(shopId)
    if json_data is None:
        return 'unknown'
    return str(json_data['productCommentSummary']['goodRate'])


# 获取每页前30条书籍信息
def shopWebsiteFirst(pageSize):
    url = "https://search.jd.com/Search?keyword=编程书籍&psort=3&wq=编程书籍&psort=3&pvid=c56b6acd7eed4fb0a1a1cbfc61ff4377&page=%d&s=121&click=0"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64',
        'cookie': '3AB9D23F7A4B3C9B=D3OAJKRHRTXMRFJZFYLTOT3HKZVMQCMGKOMQAFBWIOW7YQBZF6JP2SVV5IO5XN2ITCHJAGBW2RZ4TYJFIPDHZGJUJ4'}

    data = ''
    if os.path.exists('jd-html/' + str(pageSize) + '-coding.html'):
        print("read" + str(pageSize) + '-coding.html')
        with codecs.open('jd-html/' + str(pageSize) + '-coding.html', 'r', encoding='utf-8') as fp:
            data = fp.read()
    else:
        try:
            res = requests.get(url % pageSize, headers=headers)
            data = res.content.decode('utf-8')
        except:
            print("解码失败")
        else:
            with codecs.open('jd-html/' + str(pageSize) + '-coding.html', 'w', encoding='utf-8') as fp:
                fp.write(data)
    soup = BeautifulSoup(data, 'html.parser')
    allShop = soup.findAll('li', attrs={'class': 'gl-item'})
    return allShop


# 获取每页后三十条书籍信息
def shopWebsiteLast(pageSize):
    # 获取当前的Unix时间戳，并且保留小数点后5位
    a = time.time()
    b = '%.5f' % a
    url = 'https://search.jd.com/Search?keyword=编程书籍&psort=3&wq=编程书籍&psort=3&pvid=c56b6acd7eed4fb0a1a1cbfc61ff4377&page=' + str(
        pageSize + 1) + '&s=' + str(48 * pageSize - 20) + '&scrolling=y&log_id=' + str(b)
    header = {'authority': 'search.jd.com',
              'method': 'GET',
              'path': '/s_new.php?keyword=%E7%BC%96%E7%A8%8B%E4%B9%A6%E7%B1%8D&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E7%BC%96%E7%A8%8B%E4%B9%A6%E7%B1%8D',
              'scheme': 'https',
              'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
              'x-requested-with': 'XMLHttpRequest',
              }

    data = ''
    if os.path.exists('jd-html/' + str(pageSize + 1) + '-coding.html'):
        print("read" + str(pageSize + 1) + '-coding.html')
        with codecs.open('jd-html/' + str(pageSize + 1) + '-coding.html', 'r', encoding='utf-8') as fp:
            data = fp.read()
    else:
        try:
            res = requests.get(url, headers=header)
            data = res.content.decode('utf-8')
        except:
            print("解码失败")
        else:
            with codecs.open('jd-html/' + str(pageSize + 1) + '-coding.html', 'w', encoding='utf-8') as fp:
                fp.write(data)
    soup = BeautifulSoup(data, 'html.parser')
    allShop = soup.findAll('li', attrs={'class': 'gl-item'})
    return allShop


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


# 写入csv文件
b = [shop_info[i:i + 11] for i in range(0, len(shop_info), 11)]
with open("store/jd-item-info-coding.csv", 'w+', encoding='utf-8') as fp:
    for value in b:
        fp.write('\n')
        fp.write(",".join(value))
