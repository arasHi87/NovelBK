import redis
import scrapy
from NovelBK import settings
from scrapy_redis import get_redis

r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)

class MasterWenku8Spider(scrapy.Spider):
    name = 'master_wenku8'
    start_urls = [
        'https://www.wenku8.net/book/1.htm'
    ]

    def parse(self, response):
        is_exist = response.xpath('//div[5]/div/div/div[1]/table[1]/tr[1]/td/table/tr/td[1]/span/b/text()').get()
        aid = response.url.split('/')[-1].split('.')[0]

        if is_exist or int(aid) < settings.WENKU8_MAX_AID:
            url = response.url.replace(aid + '.htm', str(int(aid) + 1) + '.htm')
            yield scrapy.Request(url = url, callback = self.parse)
            if is_exist:
                r.lpush('NovelBK:start_urls',
                    response.xpath('//div[5]/div/div/div[1]/div[4]/div/span[1]/fieldset/div/a/@href').get())
                