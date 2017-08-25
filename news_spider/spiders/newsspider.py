#!usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author: Jeff Zhang
@date:   2017-08-23
"""

from news_spider.items import NewsItem

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
import json
import re
from scrapy import Request

def ListCombiner(lst):
    string = ""
    for e in lst:
        string += e
    return string.replace(' ','').replace('\n','').replace('\t','')\
        .replace('\xa0','').replace('\u3000','').replace('\r','')


class NeteaseNewsSpider(CrawlSpider):
    name = "netease_news_spider"
    allowed_domains = ['news.163.com']
    start_urls = ['http://news.163.com/']

    # http://news.163.com/17/0823/20/CSI5PH3Q000189FH.html
    url_pattern = r'(http://news\.163\.com)/(\d{2})/(\d{4})/\d+/(\w+)\.html'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        pattern = re.match(self.url_pattern, str(response.url))
        source = 'news.163.com'
        if sel.xpath('//div[@class="post_time_source"]/text()'):
            time = sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[0] + ' ' + sel.xpath('//div[@class="post_time_source"]/text()').extract_first().split()[1]
        else:
            time = 'unknown'
        date = '20' + pattern.group(2) + '/' + pattern.group(3)[0:2] + '/' + pattern.group(3)[2:]
        newsId = pattern.group(4)
        url = response.url
        title = sel.xpath("//h1/text()").extract()[0]
        contents = ListCombiner(sel.xpath('//p/text()').extract()[2:-3])
        comment_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{}'.format(newsId)
        yield Request(comment_url, self.parse_comment, meta={'source':source,
                                                             'date':date,
                                                             'newsId':newsId,
                                                             'url':url,
                                                             'title':title,
                                                             'contents':contents,
                                                             'time':time
                                                             })

    def parse_comment(self, response):
        result = json.loads(response.text)
        item = NewsItem()
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['url'] = response.meta['url']
        item['title'] = response.meta['title']
        item['contents'] = response.meta['contents']
        item['comments'] = result['cmtAgainst'] + result['cmtVote'] + result['rcount']
        item['time'] = response.meta['time']
        return item



class SinaNewsSpider(CrawlSpider):
    name = "sina_news_spider"
    allowed_domains = ['news.sina.com.cn']
    start_urls = ['http://news.sina.com.cn']
    # http://finance.sina.com.cn/review/hgds/2017-08-25/doc-ifykkfas7684775.shtml
    url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/(\d{4}-\d{2}-\d{2})/doc-(.*)\.shtml'
    # url_pattern = r'(http://(?:\w+\.)*news\.sina\.com\.cn)/.*/(2017-08-25)/doc-(.*)\.shtml'

    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath("//h1[@id='artibodyTitle']/text()"):
            title = sel.xpath("//h1[@id='artibodyTitle']/text()").extract()[0]
            pattern = re.match(self.url_pattern, str(response.url))
            source = pattern.group(1)
            date = pattern.group(2).replace('-','/')
            if sel.xpath('//span[@class="time-source"]/text()'):
                time = sel.xpath('//span[@class="time-source"]/text()').extract_first().split()[0]
            else:
                time = 'unknown'
            newsId = pattern.group(3)
            url = response.url
            contents = ListCombiner(sel.xpath('//p/text()').extract()[:-3])
            comment_elements = sel.xpath("//meta[@name='sudameta']").xpath('@content').extract()[1]
            comment_channel = comment_elements.split(';')[0].split(':')[1]
            comment_id = comment_elements.split(';')[1].split(':')[1]
            comment_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={}&newsid={}'.format(comment_channel,comment_id)
            yield Request(comment_url, self.parse_comment, meta={'source':source,
                                                                 'date':date,
                                                                 'newsId':newsId,
                                                                 'url':url,
                                                                 'title':title,
                                                                 'contents':contents,
                                                                 'time':time
                                                                })

    def parse_comment(self, response):
        if re.findall(r'"total": (\d*)\,', response.text):
            comments = re.findall(r'"total": (\d*)\,', response.text)[0]
        else:
            comments = 0
        item = NewsItem()
        item['comments'] = comments
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['contents'] = response.meta['contents']
        item['source'] = response.meta['source']
        item['date'] = response.meta['date']
        item['newsId'] = response.meta['newsId']
        item['time'] = response.meta['time']
        return item


class TencentNewsSpider(CrawlSpider):
    name = 'tencent_news_spider'
    # allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com']
    # http://news.qq.com/a/20170825/026956.htm
    url_pattern = r'(.*)/a/(\d{8})/(\d+)\.htm'
    rules = [
        Rule(LxmlLinkExtractor(allow=[url_pattern]), callback='parse_news', follow=True)
    ]

    def parse_news(self, response):
        sel = Selector(response)
        if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()'):
            title = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        elif sel.xpath('//*[@id="C-Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()'):
            title = sel.xpath('//*[@id="C-Main-Article-QQ"]/div/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        elif sel.xpath('//*[@id="ArticleTit"]/text()'):
            title = sel.xpath('//*[@id="ArticleTit"]/text()').extract()[0]
        else:
            title = 'unknown'
        pattern = re.match(self.url_pattern, str(response.url))
        source = pattern.group(1)
        date = pattern.group(2)
        date = date[0:4] + '/' + date[4:6] + '/' + date[6:]
        newsId = pattern.group(3)
        url = response.url
        if sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[3]/text()'):
            time = sel.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[1]/div[1]/div/div[1]/span[3]/text()').extract()[0]
        else:
            time = 'unknown'
        contents = ListCombiner(sel.xpath('//p/text()').extract()[:-8])

        if response.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()'):
            cmt = response.xpath('//*[@id="Main-Article-QQ"]/div/div[1]/div[2]/script[2]/text()').extract()[0]
            if re.findall(r'cmt_id = (\d*);', cmt):
                cmt_id = re.findall(r'cmt_id = (\d*);', cmt)[0]
                comment_url = 'http://coral.qq.com/article/{}/comment?commentid=0&reqnum=1&tag=&callback=mainComment&_=1389623278900'.format(cmt_id)
                yield Request(comment_url, self.parse_comment, meta={'source': source,
                                                                     'date': date,
                                                                     'newsId': newsId,
                                                                     'url': url,
                                                                     'title': title,
                                                                     'contents': contents,
                                                                     'time': time
                                                                     })
            else:
                item = NewsItem()
                item['source'] = source
                item['time'] = time
                item['date'] = date
                item['contents'] = contents
                item['title'] = title
                item['url'] = url
                item['newsId'] = newsId
                item['comments'] = 0
                return item

    def parse_comment(self, response):
        if re.findall(r'"total":(\d*)\,', response.text):
            comments = re.findall(r'"total":(\d*)\,', response.text)[0]
        else:
            comments = 0
        item = NewsItem()
        item['source'] = response.meta['source']
        item['time'] = response.meta['time']
        item['date'] = response.meta['date']
        item['contents'] = response.meta['contents']
        item['title'] = response.meta['title']
        item['url'] = response.meta['url']
        item['newsId'] = response.meta['newsId']
        item['comments'] = comments
        return item


class SohuNewsSpider(CrawlSpider):
    name = "sohu_news_spider"
    pass



class IfengNewsSpider(CrawlSpider):
    name = "ifeng_news_spider"
    pass


