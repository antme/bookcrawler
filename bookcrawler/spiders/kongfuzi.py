# coding=gbk
import scrapy
import string
from scrapy.spider import Spider
from scrapy.selector import Selector
from bookcrawler.items import BookcrawlerItem
from __builtin__ import len

class Kongfuzicrawler(Spider):
    name = "kongfuzi"
    host = "http://shop.kongfz.com/"
    allowed_domains = ["shop.kongfz.com"]
    isShop = "true"
    start_urls = [
        
    ]
    
    def __init__(self, start, end, isShop):
        self.isShop = isShop
        if(isShop == "true"):
            self.start_urls = [
                "http://shop.kongfz.com/shop_list_2_" +str(x) +'.html' for x in range(string.atoi(start), string.atoi(end))
            ]
        else:
            self.start_urls = [
                "http://tan.kongfz.com/shop_list_hot_p_" +str(x) +'/' for x in range(string.atoi(start), string.atoi(end))
            ]
             
    #"http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=true' for x in range(2,4)
    def parse(self, response):
        hxs = Selector(response)
        #获取所有的书店
        shopLinks = hxs.xpath('//div[@class="number_tab m_t10"]//td//a/@href')
        #open(filename, 'wb').write(response.body)
        #根据书店URL去分析书的分类
        for shopLink in shopLinks:           
            yield self.make_requests_from_url(shopLink.extract()).replace(callback=self.parseShopBookCategory)
            
            
    def parseShopBookCategory(self, response):
        hxs = Selector(response)  
        #获取书店下的所有分类          
        bookCateLins = hxs.xpath('//div[@class="module_con"]//li//a')
        
        
        for bookCatelink in bookCateLins:

            #如果是网站的分类
            if("0_0_0_0.html" in  bookCatelink.extract() or (self.isShop == "false" and "cat_" in bookCatelink.extract())):
                bookCate = bookCatelink.xpath('node()')[0].extract().encode('utf-8')
                total = filter(str.isdigit, bookCate)
                
                bookCate = bookCate.replace('(' + str(total) + ')', '')
                #过滤掉统一的“书籍”分类
                if u'\u4E66\u7C4D' in bookCatelink.xpath('node()')[0].extract():
                    continue
                
                bookCateViewUrl = bookCatelink.xpath('@href')[0].extract().encode('utf-8')
            
                #分页计算
                pages = string.atoi(total)/100 + 2
                for i in range(1, pages):
                    bookCatePageViewUrl = bookCateViewUrl
                    bookCatePageViewUrl = bookCatePageViewUrl.replace('0_1_0_','0_1_100_')                        
                    bookCatePageViewUrl = bookCatePageViewUrl.replace('0_0_0_0','0_'+ str(i) + '_0_0')
                    #根据分页信息获取书籍列表
                    request = self.make_requests_from_url(bookCatePageViewUrl).replace(callback=self.parseBookCateListPage)
                    request.meta['bookCate'] = bookCate
                    yield request
                
                
                
    def parseBookCateListPage(self, response):
        hxs = Selector(response)
        bookLinks = hxs.xpath('//div[@class="result_tit"]//a/@href')
        bookCate = response.meta['bookCate']
        #open(filename, 'wb').write(response.body)
        for booklink in bookLinks:
            bookViewUrl = booklink.extract()
            request = self.make_requests_from_url(bookViewUrl).replace(callback=self.parseBookDetail)  
            request.meta['bookCate'] = bookCate
            yield request          

   
             
    def parseBookDetail(self, response):
        hxs = Selector(response)
        bookCate = response.meta['bookCate']
        items = []
        item = BookcrawlerItem()
        if(self.isShop == "true"):
            names = hxs.xpath('//div[@class="name itemsn"]//node()')
        else:
            names = hxs.xpath('//div[@class="itemsn"]//h1//node()')
            
        if(len(names) > 0):
            item['title'] = names[0].extract().encode('utf-8')
            summary = hxs.xpath('//div[@class="text_box1 m_t10"]//p/text()')
            item['category'] = bookCate
            item['summary'] = ''
            item['catalog'] = ''
            if(len(summary) > 0):               
                for sum in summary:
                    item['summary'] = item['summary'] + '<br>' + sum.extract().encode('utf-8')
     
            catalog = hxs.xpath('//div[@class="partOrAlls"]/text()')
            if(len(catalog) > 0):                
                item['catalog'] = catalog[0].extract().encode('utf-8')
            bookInfoList = hxs.xpath('//div[@class="book_info grid_15"]//p/text()')
            item['url'] = response.url
            oid = item['url'].split("/")[-3] + "_" +  item['url'].split("/")[-2]
            item['oid'] = oid
            imageurl = hxs.xpath('//div[@id="bigBookImg"]//img/@src')
            if(len(imageurl) > 0):
                item['image'] = hxs.xpath('//div[@id="bigBookImg"]//img/@src')[0].extract().encode('utf-8')
            else:
                item['image'] = ''
                
            keyIndex = {};
            keyIndex["authors"] = u'\u4F5C\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u8005';
            keyIndex["pubdate"] = u'\u51FA\u7248\u65F6\u95F4';
            keyIndex["publisher"] = u'\u51FA \u7248 \u793E';
            keyIndex["pages"] = u'\u9875\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u6570';
            keyIndex["price"] = u'\u552E\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u4EF7';
            keyIndex["binding"] = u'\u88C5\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u8BA2';
            keyIndex["pub_version"] = u'\u7248\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u6B21';
  
            for bookInfo in bookInfoList:
                binfo = bookInfo.extract()
                if("I" in binfo and "S" in binfo and "B" in binfo and "N" in binfo ):
                    isbn = bookInfo.extract().split(u'\uFF1A')[-1].encode('utf-8')
                    if(len(isbn) > 10):
                        item["isbn13"] = isbn
                    elif(len(isbn) > 1):
                        item["isbn10"] = isbn
                    continue
                
                #印刷日期为出版日期
                if(u"\u5370\u5237\u65F6\u95F4" in binfo):
                    item["pubdate"] = bookInfo.extract().split(u'\uFF1A')[-1].encode('utf-8')
                    if(len(item["pubdate"]) > 0):
                        continue
                
                for key in keyIndex:
                    if keyIndex[key] in bookInfo.extract() :  
                        if(key == 'price'):
                            item[key]  = hxs.xpath('//span[@class="red font16 m_r10"]/text()')[0].extract()
                        elif(key == 'pubdate'):
                            pubdates = hxs.xpath('//div[@class="grid_7 m_r10"]//p//a/text()')
                            pdate = ""
                            #获取带A标签的日期
                            if(len(pubdates) > 0):
                                for pubd in pubdates:
                                    if(len(pdate) >0):
                                        pdate = pdate + "-" + pubd.extract()
                                    else:
                                        pdate = pubd.extract()
                                        
                            if(len(pdate) < 1):
                                #获取字符串的日期
                                item[key] = bookInfo.extract().split(u'\uFF1A')[-1].encode('utf-8')                                
                            else:
                                item[key] = pdate
                            
                            
                        else:
                            item[key] = bookInfo.extract().split(u'\uFF1A')[-1].encode('utf-8')
                            
                        break             
                                  
            items.append(item) 
        return items
    
    
    def parseBookListPage(self, response):
        hxs = Selector(response)
        bookLinks = hxs.xpath('//div[@class="result_tit"]//a/@href')
        for booklink in bookLinks:
            bookViewUrl = booklink.extract()
            yield self.make_requests_from_url(bookViewUrl).replace(callback=self.parseBookDetail)
