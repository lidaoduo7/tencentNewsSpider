# -*- coding: utf-8 -*-
import scrapy
from spider_news.items import SpiderNewsItem
import re
from scrapy.http import Request
from scrapy.selector import Selector
import requests
import json
import codecs
import os
import datetime

class TencentSpiderSpider(scrapy.Spider):
    name = 'tencent_spider'
    allowed_domains = ['new.qq.com']
    start_urls = ['https://news.qq.com/']

    # https://news.qq.com/a/20180120/000738.htm     只匹配这种类型的数据
    url_pattern = r'http://new\.qq\.com/(\w+)/(\d{8})/(\w+)\.html'


    def parse(self, response):
        '''
        从腾讯新闻首页获取新闻链接地址，回调
        :param response:
        :return:
        '''
        pat = re.compile(self.url_pattern)
        next_urls = re.findall(pat, str(response.body))   #

        for next_url in next_urls:
            article = 'http://new.qq.com/' + next_url[0] + '/' + next_url[1] + "/" + next_url[2] + '.html'
            # print(article)
            yield Request(article, callback=self.parse_news)  #

    def parse_news(self, response):
        '''
        每个新闻网页，解析出新闻的时间，标题，正文，评论页面链接，
        :param response:
        :return:
        '''
        item = SpiderNewsItem()
        selector = Selector(response)

        url_pattern2 = r'(\w+)://(\w+)\.qq\.com/(\w+)/(\d{8})/(\w+)\.html'
        pattern = re.match(url_pattern2, str(response.url))
        # print(pattern)
        date = pattern.group(4)   #日期
        newsId = pattern.group(5) #newsID
        news_link = str(response.url)

        pubtime = re.findall(re.compile(r'"pubtime": "(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})"'), str(response.text))
        cmtid = re.findall(re.compile(r'"comment_id": "(\d+)"'),str(response.text))
        # print('cmt'+ str(cmtid[0]))
        comments_link = 'http://coral.qq.com/'+cmtid[0]   #评论的链接地址
        title = re.findall(re.compile(r'"title": "(.*)"'), str(response.text))   #
        # print('title'+ str(title[0]))
        passage = re.findall(re.compile(r'<p class="one-p">(.*)</p>'),str(response.text))
        res_str = ''
        for every_pas in passage:
            res_str += every_pas
        # print(res_str)

        comments_recent = self.crawlcomment(cmtid[0])
        item['comments'] = comments_recent


        item['pubtime'] = pubtime[0]
        source = 'Tencent'
        item['source'] = source
        item['title'] = str(title[0])
        item['date'] = date
        # item['newsId'] = newsId
        item['news_link'] = news_link                #新闻的链接地址
        item['comments_link'] =  comments_link  #评论的链接地址
        # item['contents'] = {'link': str(response.url), 'title': u'', 'passage': u''}       #嵌套结构的创建
        # item['contents'] = {'link': str(response.url),  'passage': u''}
        # item['contents']['passage'] = res_str
        item['contents'] = res_str
        yield item



    # 爬取新闻评论id为commentid的所有评论
    def crawlcomment(self,commentid):
        '''
        真正的请求地址
        http://coral.qq.com/3085995965
        http://coral.qq.com/article/3085995965/comment/v2?callback=_article3085995965commentv2&orinum=10&oriorder=o&pageflag=1&cursor=0&scorecursor=0&orirepnum=2&reporder=o&reppageflag=1&source=1&_=1536648805027
        解析参考 https://www.cnblogs.com/bigyang/p/8941672.html
        :param date:
        :param newsID:
        :return:
        '''
        url1 = 'http://coral.qq.com/article/' + commentid + '/comment/v2?callback=_article'+ commentid + 'commentv2&orinum=10&oriorder=o&pageflag=1&cursor='
        url2 = '&orirepnum=10&_=1522383466213'
        # 一定要加头要不然无法访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        response = self.getHTMLText(url1 + '0' + url2, headers)

        result = []

        while 1:
            pattern = "_article" + commentid + "commentv2\\((.+)\\)"
            # g = re.search("_articlecommentv2\\((.+)\\)", response)
            g = re.search(pattern, response)
            out = json.loads(g.group(1))
            if not out["data"]["last"]:
                print("finish！")
                break;
            for i in out["data"]["oriCommList"]:
                time = str(datetime.datetime.fromtimestamp(int(i["time"])))  # 将unix时间戳转化为正常时间
                line = json.dumps(time + ':' + i["content"], ensure_ascii=False) + '\n'
                # print(i["content"])
                result.append(i["content"])

            url = url1 + out["data"]["last"] + url2  # 得到下一个评论页面链接
            # print("下一个评论页面链接")
            # print(url)
            response = self.getHTMLText(url, headers)
            return result

    def getHTMLText(self,url, headers):
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            return "产生异常 "






