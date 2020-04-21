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
        '''
        b_name: book name
        c_name: chapter name
        v_name: volume name
        '''

        aid = response.url.split('/')[-2]
        b_name = response.xpath('//*[@id="title"]/text()').get()
        
        # build index information
        temp = []
        item = Wenku8IndexItem()
        item['index'] = {}
        item['index'][b_name] = []

        for ele in response.xpath('//table/tr/td'):
            n_type = ele.xpath('@class').get()
            if n_type == 'vcss':
                if temp:
                    item['index'][b_name].append(temp)
                temp = [normalize('NFKD', ele.xpath('text()').get())]
            else:
                if ele.xpath('a/text()').get():
                    c_name = normalize('NFKD', ele.xpath('a/text()').get())
                    temp.append(c_name)

        item['index'][b_name].append(temp)
        # yield item

        url_check_list = [response.url.replace('index.htm', x.get()) for x in response.xpath("//table/tr/td[@class='ccss']/a/@href")]

        # get content
        for x in response.xpath("//table/tr/td[@class='ccss']/a"):
            vid = x.xpath('@href').get().replace('.htm', '')
            c_name = x.xpath('text()').get()
            url = response.url.replace('index', vid)
            if not self.server.hget(self.settings.get('REDIS_DATA_DICT'), url) or self.settings.get('DEBUG_MOD'):
                yield Request(
                    url = url,
                    meta = {
                        'aid': aid,
                        'vid': vid,
                        'c_name': normalize('NFKD', c_name),
                        'b_name': b_name,
                        'item': item,
                        'url_check_list': url_check_list
                    },
                    callback = self.parse_chapter
                )
    
    def parse_chapter(self, response):
        cc = OpenCC('s2t')
        loc = os.path.dirname(__file__)
        content = BeautifulSoup(response.xpath('//*[@id="content"]').get().strip(), "lxml").text
        title = normalize('NFKD', response.xpath('//*[@id="title"]/text()').get())
        v_name = "".join(title.rsplit(response.meta['c_name'], 1)).strip()
        path = os.path.join(loc, '../data/wenku8', response.meta['b_name'], 'txt', v_name)

        if not os.path.isdir(path):
            os.makedirs(path)

        if '因版权问题，文库不再提供该小说的阅读！' in content:
            url = self.settings.get('WENKU8_DOWNLOAD_URL').format(
                response.meta['aid'],
                response.meta['vid'])
            urlretrieve(url, filename = os.path.join(path, response.meta['v_name'] + '.txt'))
        else:
            if response.meta['c_name'] != '插图':
                with open(os.path.join(path, response.meta['c_name'] + '.txt'), 'w+') as fp:
                    fp.write(cc.convert(content))
            else:
                with open(os.path.join(path, response.meta['c_name'] + '.txt'), 'w+') as fp:
                    for img in response.xpath('//*[@class="divimage"]').getall():
                        fp.write(img)
        
        self.server.hset(self.settings.get('REDIS_DATA_DICT'), response.url, 0)
        file_status = True

        for url in response.meta['url_check_list']:
            if not self.server.hget(self.settings.get('REDIS_DATA_DICT'), url):
                file_status = False
                break
        
        if file_status:
            yield response.meta['item']