# -*- coding: utf-8 -*-
import redis
import scrapy
import threadpool
from BearCat2.LOG import log
from BearCat2.settings import REDIS_DB
from BearCat2.settings import REDIS_HOST
from BearCat2.settings import REDIS_PORT
from BearCat2.settings import THREADPOOL
from BearCat2.settings import REDIS_PARAMS
from BearCat2.settings import REDIS_MAXCONNECTIONS
from BearCat2.settings import REDIS_CONNECT_TIMEOUT
from BearCat2.Commom import parse_pool


class A66ipSpider(scrapy.Spider):
    pool_redis = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PARAMS,
                                      decode_responses=True,
                                      max_connections=REDIS_MAXCONNECTIONS,
                                      socket_connect_timeout=REDIS_CONNECT_TIMEOUT)
    r = redis.Redis(connection_pool=pool_redis)
    pool = threadpool.ThreadPool(THREADPOOL)
    name = 'a66ip'
    allowed_domains = ['www.66ip.cn/']

    # start_urls = ['http://www.66ip.cn/']
    def start_requests(self):
        for num in range(1, 11):
            url = (f'http://www.66ip.cn/{num}.html')
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        log(f'{self.name}抓取代理成功')
        proxies_list = []
        proxy = response.xpath('//tr')[1:]
        for i in proxy:
            http = i.xpath('./td/text()')[3].get()
            if '高匿' in http:
                ip = i.xpath('./td/text()')[0].get()
                host = i.xpath('./td/text()')[1].get()
                save = ip, host
                proxies = save[0] + ':' + save[1]
                proxies_list.append(proxies)
        proxies_lists = [[self.name, i] for i in proxies_list]
        theading = threadpool.makeRequests(parse_pool, proxies_lists)
        for i in theading:
            self.pool.putRequest(i)
        self.pool.wait()
