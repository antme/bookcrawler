# coding=gbk
import scrapy
import string
import json
from scrapy.spider import Spider
from scrapy.selector import Selector
from bookcrawler.items import BookcrawlerItem
from __builtin__ import len

class Bookcrawler(Spider):
    name = "chaoxing"
    host = "http://book.chaoxing.com"
    allowed_domains = ["chaoxing.com"]
    start_urls = [
       
    ]
    
    def __init__(self, isvip):
        if(isvip == 'true'):
            self.start_urls = [
                "http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=true' for x in range(0,10485)
            ]
        elif(isvip == 'false'):
            self.start_urls = [
                "http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=false' for x in range(0,10001)
            ]
        else:
            self.start_urls = [
                "http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=false' for x in range(10000,20001)
            ]
            
    #"http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=true' for x in range(2,4)
    def parse(self, response):
        print self.start_urls
        hxs = Selector(response)
        bookLins = hxs.xpath('//div[@class="tit"]//a/@href')
        #open(filename, 'wb').write(response.body)
        for booklink in bookLins:
            bookViewUrl = self.host + booklink.extract()
            yield self.make_requests_from_url(bookViewUrl).replace(callback=self.parseBook)
            
    def parseReadCount(self, response):
        data = response.body
        #这里写正则匹配或者选择XPathSelector获取需要捕获的数据,略
        ajaxdata = json.loads(data)
        item = response.meta['item']
        item['read_count'] = ajaxdata['readCount']
        
        return item
               
    def parseBookScore(self, response):
        data = response.body
        #这里写正则匹配或者选择XPathSelector获取需要捕获的数据,略
        ajaxdata = json.loads(data)
        item = response.meta['item']
        item['rating_average'] = ajaxdata['avgScore']
        item['total_score'] = ajaxdata['totalScore']
        item['rater_count'] = ajaxdata['userCount']
        return item
    
    def parseBookReadStatus(self, response):
        data = response.body
        data = data[1:-1]
        #这里写正则匹配或者选择XPathSelector获取需要捕获的数据,略
        ajaxdata = json.loads(data)
        item = response.meta['item']
        item['read_complete_count'] = ajaxdata['completeCount']
        item['read_progress_count'] = ajaxdata['progressCount']
        return item
        
    
        
    def parseBook(self, response):
        hxs = Selector(response)
        items = []
        item = BookcrawlerItem()
        names = hxs.xpath('//div[@class="box_title"]//h1/text()')
        if(len(names) > 0):
            item['title'] = names[0].extract().encode('utf-8')
            summary = hxs.xpath('//div[@class="part"]/text()')
            item['summary'] = ''
            item['catalog'] = ''
            if(len(summary) > 0):
                item['summary'] = summary[0].extract().encode('utf-8')
                
            catalog = hxs.xpath('//div[@class="partOrAlls"]/text()')
            if(len(catalog) > 0):                
                item['catalog'] = catalog[0].extract().encode('utf-8')
            bookInfoList = hxs.xpath('//div[@class="bokts_list"]//li')
            item['url'] = response.url
            oid = item['url'].split("/")[-1].split(".")[0].split("_")[1]
            ssid = oid[1:9]
            item['oid'] = oid
            item['image'] = hxs.xpath('//div[@class="bokts"]//div[@class="pro"]//img/@src')[0].extract().encode('utf-8')
            
            keyIndex = {};
            keyIndex["authors"] = u'\u4F5C\u8005';
            keyIndex["pubdate"] = u'\u51FA\u7248\u65E5\u671F';
            keyIndex["publisher"] = u'\u51FA\u7248\u793E';
            keyIndex["pages"] = u'\u9875\u6570';
            keyIndex["category"] = u'\u6240\u5C5E\u5206\u7C7B';

      
            
            for bookInfo in bookInfoList:
                infoItems = bookInfo.xpath('node()')
                for key in keyIndex:
                    if keyIndex[key] in infoItems[0].extract() :
                        if(len(infoItems) > 1):                           
                            if(key == 'category'):
                                categoryInfo = infoItems[1].xpath('node()')
                                item['category'] = categoryInfo[0].extract().encode('utf-8')
                            else:    
                                item[key] = infoItems[1].extract().encode('utf-8')
                                  
                        break
                    
            getBookReadCountUrl = 'http://book.chaoxing.com/ebook/getBookReadCount.do?ssID=' + ssid
            request = self.make_requests_from_url(getBookReadCountUrl).replace(callback=self.parseReadCount)
            request.meta['item'] = item
            yield request
            
            getBookReadCountUrl = 'http://book.chaoxing.com/getBookScore.do?ssID=' + ssid
            request = self.make_requests_from_url(getBookReadCountUrl).replace(callback=self.parseBookScore)
            request.meta['item'] = item
            yield request
                       
            getBookReadCountUrl = 'http://plan.chaoxing.com/planstates.jhtml?uniqueUrl=http://book.chaoxing.com/ebook/read_' +ssid + '.html'
            request = self.make_requests_from_url(getBookReadCountUrl).replace(callback=self.parseBookReadStatus)
            request.meta['item'] = item
            yield request         
                       
            items.append(item) 
               
        
