# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class NewsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    source = Field()
    date = Field()
    newsId = Field()
    title = Field()
    contents = Field()
    url = Field()
    comments = Field()
    time = Field()


class TencentRollNewsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    date = Field()
    time = Field()
    title = Field()
    newsId = Field()
    contents = Field()
    comments = Field()
    source = Field()
    column = Field()
    category = Field()