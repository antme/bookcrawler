# coding=gbk
import scrapy
import fileinput
import pymongo
import json
import string
from scrapy.spider import Spider
from scrapy.selector import Selector
from bookcrawler.items import BookcrawlerItem
from __builtin__ import len

class Storecrawler(Spider):
    name = "store"
    host = "http://shop.kongfz.com/"
    allowed_domains = ["shop.kongfz.com"]
    isShop = "true"
    start_urls = [
        
    ]
    
    def __init__(self, isShop):
        self.isShop = isShop
        if(isShop == "true"):
            self.start_urls = [
                "http://shop.kongfz.com/shop_list_2_" +str(x) +'.html' for x in range(0, 81)
            ]
        else:
            self.start_urls = [
                "http://tan.kongfz.com/shop_list_hot_p_" +str(x) +'/' for x in range(0, 115)
            ]
            
        self.connection=pymongo.Connection('localhost',27017)
        self.db=self.connection.book
        self.storeconnenction = self.db.store
        
             
    def parse(self, response):
        hxs = Selector(response)
        shopLinks = hxs.xpath('//div[@class="number_tab m_t10"]//td//a')
        for shopLink in shopLinks:
            name = shopLink.select("text()").extract()[0].encode('utf-8')
            url = shopLink.select("@href").extract()[0]
            storeid = url.split("/")[-2]
            store = {"name":name, "url":url, "storeid":storeid}
            document = self.storeconnenction.find_one({"storeid": storeid})
            if(not document):
                self.storeconnenction.insert(store)
  
            
            
            