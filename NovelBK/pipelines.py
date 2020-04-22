# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import redis
import pymongo
from scrapy import Request
from NovelBK.utils import *
from NovelBK import settings
from NovelBK.items import Wenku8IndexItem
from scrapy.exporters import JsonItemExporter

class Wenku8IndexPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Wenku8IndexItem):
            b_name, content = list(item['index'].items())[0]
            client = pymongo.MongoClient("mongodb://{}:{}@{}:{}".format(
                settings.DB_USER,
                settings.DB_PWD,
                settings.DB_HOST,
                settings.DB_PORT
            ))
            db = client[settings.DB_NAME]
            col = db['wenku8']
            data = {
                'b_name': b_name,
                'author': content['author'],
                'index': json.dumps(content['index'], ensure_ascii = False)
            }
            
            if not col.find({'b_name': b_name}).count():
                col.insert_one(data)
            else:
                col.update_one({'b_name': b_name}, {'$set': {'index': data['index']}})

            txt2epub(item, os.path.join(loc, 'data/wenku8'))

        return item
    
    def open_spider(self, spider):
        r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)
        if r.hlen(settings.REDIS_DATA_DICT) == 0:
            r.hset(settings.REDIS_DATA_DICT, 'field', 0)