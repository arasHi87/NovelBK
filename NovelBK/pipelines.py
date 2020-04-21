# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import redis
from scrapy import Request
from NovelBK.utils import *
from NovelBK import settings
from NovelBK.items import Wenku8IndexItem
from scrapy.exporters import JsonItemExporter

class Wenku8IndexPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Wenku8IndexItem):
            b_name, content = list(item['index'].items())[0]
    
            loc = os.path.dirname(__file__)
            path = os.path.join(loc, 'data/data.json')
            data = json.load(open(path))
            data['wenku8'][b_name] = content

            with open(path, 'w') as fp:
                fp.write(json.dumps(data, ensure_ascii = False, indent = 4))

            txt2epub(item, os.path.join(loc, 'data/wenku8'))

        return item
    
    def open_spider(self, spider):
        r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)
        if r.hlen(settings.REDIS_DATA_DICT) == 0:
            r.hset(settings.REDIS_DATA_DICT, 'field', 0)