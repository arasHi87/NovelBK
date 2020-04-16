import os
import re
from scrapy import Request
from NovelBK import settings
from bs4 import BeautifulSoup
from NovelBK.items import Wenku8IndexItem
from urllib.request import urlretrieve
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
                temp = [ele.xpath('text()').get()]
            else:
                n_name = ele.xpath('a/text()').get()
                if n_name != '插图' and n_name:
                    temp.append(n_name)
        yield item

        # get content
        for x in response.xpath("//table/tr/td[@class='ccss']/a"):
            vid = x.xpath('@href').get().replace('.htm', '')
            vname = x.xpath('text()').get()
            url = response.url.replace('index', vid)
            yield Request(
                url = url,
                meta = {
                    'aid': aid,
                    'vid': vid,
                    'vname': vname,
                    'book_name': book_name
                },
                callback = self.parse_chapter
            )
    
    def parse_chapter(self, response):
        content = BeautifulSoup(response.xpath('//*[@id="content"]').get(), "lxml").text
        chapter = "".join(response.xpath('//*[@id="title"]/text()').get().rsplit(response.meta['vname'], 1)).strip()
        path = os.path.join('data', response.meta['book_name'], chapter)

        if not os.path.isdir(path):
            os.makedirs(path)

        if '因版权问题，文库不再提供该小说的阅读！' in content:
            url = settings.WENKU8_DOWNLOAD_URL.format(
                    response.meta['aid'],
                    response.meta['vid'])
            urlretrieve(url, filename = os.path.join(path, response.meta['vname'] + '.txt'))
        else:
            if response.meta['vname'] != '插图':
                with open(os.path.join(path, response.meta['vname'] + '.txt'), 'w+') as fp:
                    fp.write(content)
