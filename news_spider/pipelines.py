# -*- coding: gbk -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import os


class NewsSpiderPipeline(object):
    def __init__(self):
        self.current_dir = os.getcwd()

    def process_item(self, item, spider):
        dir_path = self.current_dir + '/docs' + item['source'] + '/' + item['date']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        news_file_path = dir_path + '/' + item['newsId'] + '.json'
        if os.path.exists(news_file_path) and os.path.isfile(news_file_path):
            print('---------------------------------------')
            print(item['newsId'] + '.json exists, not overriden')
            print('---------------------------------------')
            return item


        news_file = codecs.open(news_file_path, 'w', 'gbk')
        line = json.dumps(dict(item))
        news_file.write(line)
        news_file.close()
        return item
