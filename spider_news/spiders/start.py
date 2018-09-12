# -*- coding: utf-8 -*-

from scrapy import cmdline


'''

scrapy crawl tencent_spider
scrapy crawl tencent_spider -o test.json
scrapy crawl tencent_spider -o test.csv
'''



cmdline.execute("scrapy crawl tencent_spider".split())