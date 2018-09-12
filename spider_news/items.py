# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderNewsItem(scrapy.Item):

    title = scrapy.Field()         #新闻标题
    news_link = scrapy.Field()     #新闻链接地址
    # newsId = scrapy.Field()
    date = scrapy.Field()          #新闻发布日期
    source = scrapy.Field()        #新闻来源
    contents = scrapy.Field()      #正文内容
    comments_link = scrapy.Field()  # 评论页ID
    comments = scrapy.Field()     #评论内容
    pubtime = scrapy.Field()


