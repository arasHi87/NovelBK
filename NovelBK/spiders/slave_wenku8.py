import os
import re
from opencc import OpenCC
from scrapy import Request
from bs4 import BeautifulSoup
from unicodedata import normalize
from urllib.request import urlretrieve
from NovelBK.items import Wenku8IndexItem
from scrapy_redis.spiders import RedisSpider

class Wenku8SlaveSpider(RedisSpider):
    name = 'slave_wenku8'
    redis_key = 'NovelBK:start_urls'
    allow_domains = ['wenku8.net']

    def parse(self, response):
        aid =  response.url.split('/')[-2]
        book_name = response.xpath('//*[@id="title"]/text()').get()

        # build index information
        i_chapter = ''
        temp = []
        item = Wenku8IndexItem()
        item['index'] = {}
        item['index'][book_name] = []
        for ele in response.xpath('//table/tr/td'):
            n_type = ele.xpath('@class').get()
            if n_type == 'vcss':
                if temp:
                    item['index'][book_name].append(temp)
                temp = [normalize('NFKD', ele.xpath('text()').get())]
            else:
                if ele.xpath('a/text()').get():
                    n_name = normalize('NFKD', ele.xpath('a/text()').get())
                    if n_name != '插图':
                        temp.append(n_name)
        item['index'][book_name].append(temp)
        yield item

        # get content
        for x in response.xpath("//table/tr/td[@class='ccss']/a"):
            vid = x.xpath('@href').get().replace('.htm', '')
            vname = x.xpath('text()').get()
            url = response.url.replace('index', vid)

            if not self.server.hget(self.settings.get('REDIS_DATA_DICT'), url):
                yield Request(
                    url = url,
                    meta = {
                        'aid': aid,
                        'vid': vid,
                        'vname': normalize('NFKD', vname),
                        'book_name': book_name
                    },
                    callback = self.parse_chapter
                )
    
    def parse_chapter(self, response):
        cc = OpenCC('s2t')
        content = BeautifulSoup(response.xpath('//*[@id="content"]').get().strip(), "lxml").text
        chapter = "".join(normalize('NFKD',
            response.xpath('//*[@id="title"]/text()').get()).rsplit(response.meta['vname'], 1)).strip()
        path = os.path.join('data', response.meta['book_name'], chapter)

        if not os.path.isdir(path):
            os.makedirs(path)

        if '因版权问题，文库不再提供该小说的阅读！' in content:
            url = self.settings.get('WENKU8_DOWNLOAD_URL').format(
                    response.meta['aid'],
                    response.meta['vid'])
            urlretrieve(url, filename = os.path.join(path, response.meta['vname'] + '.txt'))
        else:
            if response.meta['vname'] != '插图':
                with open(os.path.join(path, response.meta['vname'] + '.txt'), 'w+') as fp:
                    fp.write(cc.convert(content))

        self.server.hset(self.settings.get('REDIS_DATA_DICT'), response.url, 0)