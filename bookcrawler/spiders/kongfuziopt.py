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
from glob import glob 

class Kongfuzioptcrawler(Spider):
    name = "kongfuziopt"
    host = "http://shop.kongfz.com/"
    allowed_domains = ["shop.kongfz.com"]
    start_urls = [
        
    ]
    
    
    def __init__(self):
        self.start_urls = [
            "http://shop.kongfz.com"
        ]
        self.connection=pymongo.Connection('localhost',27017)
        self.db=self.connection.book
        self.bookcollection = self.db.book
        self.storeconnenction = self.db.store
        #self.bookcollection.remove({})

    #"http://book.chaoxing.com/ebook/list_0__page_" +str(x) +'.html?vip=true' for x in range(2,4)
    
    def saveBookWithIsbn(self, order):
    
        lines = fileinput.input(glob(r'/Users/ymzhou/Documents/workspace/bookcrawler/k*.json'))
        for line in lines:

            if(line.startswith('[')):
                line = line[1:]
                
            line = line.replace('},', '}')
            
            if('}]' in line):
                line = line.replace('}]', '}')
                   
            jsonstr = json.loads(line)
            
            if(not 'title' in jsonstr):
                jsonstr['title'] = ''
                
            if(not 'authors' in jsonstr):
                jsonstr['authors'] = ''
                
            else:
                jsonstr['authors'] = self.parserAuthorName(jsonstr['authors'])
                    
                    
            if(not 'publisher' in jsonstr):
                jsonstr['publisher'] = ''
                
            if(not 'summary' in jsonstr):
                jsonstr['summary'] = ''
                
            if(not 'pubdate' in jsonstr):
                jsonstr['pubdate'] = ''
                    
            key = ''
            value = ''
            if('isbn10' in jsonstr):
                key = 'isbn10'
                value = jsonstr['isbn10']
            
            if('isbn13' in jsonstr):
                key = 'isbn13'
                value = jsonstr['isbn13']
                
            
            if(order == 0):
                if(len(jsonstr['summary']) < 100 or len(jsonstr['pubdate']) < 1):
                    continue
            
            if(order == 1):
                if(len(jsonstr['pubdate']) < 1 or len(jsonstr['summary']) < 1):
                    continue

            if(order == 2):
                if(len(jsonstr['pubdate']) < 1):
                    continue
            
                    
            if( key !=""):    
                document = self.bookcollection.find_one({key: value})
                if(not document):
                    self.setStoreInfo(jsonstr)
                    self.bookcollection.insert(jsonstr)
                    
            elif(order == 3):
                title = ""
                authors = ""
                publisher = ""
                               
                if('title' in jsonstr):
                    title =  jsonstr['title']
                
                if('authors' in jsonstr):
                    authors =  jsonstr['authors']
                    
                    
                if('publisher' in jsonstr):
                    publisher =  jsonstr['publisher']
  
                document = self.bookcollection.find_one({'title': title, 'authors':authors, "publisher":publisher})
                if(not document):
                    self.setStoreInfo(jsonstr)
                    self.bookcollection.insert(jsonstr)
                    
        
             
    def parserAuthorName(self, authorName):
        auname = authorName
        if(len(authorName) > 0):
            auname = authorName.replace(u' 著', '')
            auname = auname.replace(u'著', '')
            
        return auname
            
        
    def setStoreInfo(self, jsonstr):
        bookUrl = jsonstr['oid']
        storeid = bookUrl.split('_')[0]
        document = self.storeconnenction.find_one({"storeid": storeid})
        if(document):
            jsonstr['store_name'] = document['name']
            jsonstr['store_url'] = document['url']
            
            
            
        
    def saveBookWithName(self):
        lines = fileinput.input(glob(r'/Users/ymzhou/Documents/workspace/bookcrawler/kongfuzi*.json'))
        i = 0
        f = open("ana.log", 'wr')
        for line in lines:

            if(line.startswith('[')):
                line = line[1:]
            
            line = line.replace('},', '}')
            
            if('}]' in line):
                line = line.replace('}]', '}')
              
            jsonstr = json.loads(line)
            if(not ('isbn10' in jsonstr or 'isbn13' in jsonstr)):
                title = ""
                authors = ""
                publisher = ""
                               
                if('title' in jsonstr):
                    title =  jsonstr['title']
                
                if('authors' in jsonstr):
                    authors =  self.parserAuthorName(jsonstr['authors'])
                    
                    
                if('publisher' in jsonstr):
                    publisher =  jsonstr['publisher']
                    
                print title.encode('utf-8') + "================" +  authors.encode('utf-8') + "================" + publisher.encode('utf-8')
                f.write(title.encode('utf-8') + "================" +  authors.encode('utf-8') + "================" + publisher.encode('utf-8') + "\n")
                i = i + 1
                if(i > 500):                   
                    break
                
            
                        
    def parse(self, response):
        #self.saveBookWithIsbn()
        self.saveBookWithIsbn(0)
        self.saveBookWithIsbn(1)
        self.saveBookWithIsbn(2)
        self.saveBookWithIsbn(3)
        

