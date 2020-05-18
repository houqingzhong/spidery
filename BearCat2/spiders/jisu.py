# -*- coding: utf-8 -*-
import redis
import scrapy
import threadpool
from Commom.LOG import log
from Commom.Parse_pool import parse_pool
from BearCat2.settings import REDIS_DB
from BearCat2.settings import REDIS_HOST
from BearCat2.settings import REDIS_PORT
from BearCat2.settings import THREADPOOL
from BearCat2.settings import REDIS_PARAMS
from BearCat2.settings import REDIS_MAXCONNECTIONS
from BearCat2.settings import REDIS_CONNECT_TIMEOUT


class JisuSpider(scrapy.Spider):
    pool_redis = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PARAMS,
                                      decode_responses=True,
                                      max_connections=REDIS_MAXCONNECTIONS,
                                      socket_connect_timeout=REDIS_CONNECT_TIMEOUT)
    r = redis.Redis(connection_pool=pool_redis)
    pool = threadpool.ThreadPool(THREADPOOL)
    name = 'jisu'
    allowed_domains = ['www.superfastip.com/welcome/freeip']

    def start_requests(self):
        for num in range(1, 11):
            url = (f'http://www.superfastip.com/welcome/freeip/{num}')
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        log(f'{self.name}抓取代理成功')
        proxies_list = []
        proxy = response.xpath('//tr')[5:]
        for i in proxy:
            ip = i.xpath('./td/text()').get()
            host = i.xpath('./td/text()')[1].get()
            save = ip, host
            proxies = save[0] + ':' + save[1]
            proxies_list.append(proxies)
        proxies_lists = [[self.name, i] for i in proxies_list]
        theading = threadpool.makeRequests(parse_pool, proxies_lists)
        for i in theading:
            self.pool.putRequest(i)
        self.pool.wait()
