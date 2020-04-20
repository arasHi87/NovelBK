# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
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
            json_file_path = os.path.join(loc, 'data/wenku8', b_name)

            if not os.path.isdir(json_file_path):
                os.makedirs(json_file_path)

            json_file_nod = os.path.join(json_file_path, b_name +  '.json')

            if not os.path.exists(json_file_nod):
                os.mknod(json_file_nod)

            self.file = open(json_file_nod, 'wb+')
            self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
            self.exporter.start_exporting()
            self.exporter.export_item(item['index'])
            self.exporter.finish_exporting()
            self.file.close()

            # chake file exists and make epub file
            for volume in content:
                v_name = volume[0]
                file_status = True
                volume = volume[1:]

                if file_status:
                    for c_name in volume:
                        if not os.path.exists(os.path.join(json_file_path, 'txt', v_name, c_name + '.txt')):
                            file_status = False
                            break
                else:
                    break
                
            if file_status:
                txt2epub(item, os.path.join(loc, 'data/wenku8'))

        return item
    
    def open_spider(self, spider):
        r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)
        if r.hlen(settings.REDIS_DATA_DICT) == 0:
            r.hset(setting.REDIS_DATA_DICT, 'field', 0)