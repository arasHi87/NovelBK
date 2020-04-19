# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import redis
from scrapy import Request
from NovelBK import settings
from NovelBK.items import Wenku8IndexItem
from scrapy.exporters import JsonItemExporter

class Wenku8IndexPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Wenku8IndexItem):
            book_name, content = list(item['index'].items())[0]
            json_file_path = os.path.join('data', book_name, book_name +  '.json')

            # here is weird, wb+ can't create file, maybe something weong lol
            if not os.path.exists(json_file_path):
                os.mknod(json_file_path)

            self.file = open(json_file_path, 'wb')
            self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
            self.exporter.start_exporting()
            self.exporter.export_item(item['index'])
            self.exporter.finish_exporting()
            self.file.close()
        return item
    
    def open_spider(self, spider):
        r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)
        if r.hlen(settings.REDIS_DATA_DICT) == 0:
            r.hset(setting.REDIS_DATA_DICT, 'field', 0)