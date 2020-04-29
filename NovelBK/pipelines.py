# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import redis
import shutil
import gridfs
import logging
import pymongo
from scrapy import Request
from NovelBK.utils import *
from NovelBK import settings
from NovelBK.items import Wenku8IndexItem
from scrapy.exporters import JsonItemExporter

class Wenku8IndexPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Wenku8IndexItem):
            loc = os.path.dirname(__file__)
            logger = logging.getLogger('Wenku8SlaveSpider')
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
            
            # insert/update book index to database
            if not col.find({'b_name': b_name}).count():
                col.insert_one(data)
            else:
                col.update_one({'b_name': b_name}, {'$set': {'index': data['index']}})

            # save epub to database
            try:
                txt2epub(item, os.path.join(loc, settings.TEMP_STORE_PATH))
                fs = gridfs.GridFS(db, 'wenku8_file')
                
                for volume in content['index']:
                    epub_name = b_name + volume[0] + '.epub'
                    query = {'filename': epub_name}

                    if fs.exists(query):
                        fs.delete(fs.find_one(query)._id)
                    
                    with open(os.path.join(loc, settings.TEMP_STORE_PATH, b_name, 'epub', epub_name), 'rb') as fp:
                        _id = fs.put(fp.read(), filename = epub_name)
                        logger.info('save {} successful, ObjID is {}'.format(epub_name, _id))
                        fp.close()                        
            except:
                logger.warn('Error happend when making epub or insert data, please try later')

        return item
    
    def open_spider(self, spider):
        loc = os.path.dirname(__file__)
        path = os.path.join(loc, settings.TEMP_STORE_PATH)
        if not os.path.isdir(path):
            os.mkdir(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)

        r = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT)
        if r.hlen(settings.REDIS_DATA_DICT) == 0:
            r.hset(settings.REDIS_DATA_DICT, 'field', 0)
    
    def close_spider(self, spider):
        shutil.rmtree(os.path.join(
            os.path.dirname(__file__),
            settings.TEMP_STORE_PATH
        ))