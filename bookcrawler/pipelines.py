# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
class BookcrawlerPipeline(object):
    def process_item(self, item, spider):
        #filename = item['url'].split("/")[-1].split(".")[0].split("_")[1]
        #filename = "chaoxing" + "/" + filename + ".json"
        #dirName = os.path.dirname(filename)
        #if not os.path.exists(dirName):
            #os.makedirs(dirName)
        
        #open(filename, 'wb').write(item)
        return item
