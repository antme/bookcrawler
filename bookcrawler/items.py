# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class BookcrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    id = Field()
    oid = Field()
    catalog = Field()
    summary = Field()
    price = Field()
    pubdate = Field()
    publisher = Field()
    translators = Field()
    image = Field()
    url = Field()
    subtitle = Field()       
    title = Field()
    pages = Field()
    author_intro = Field()
    authors = Field()
    category = Field()
    rater_count = Field()
    rating_average = Field()
    read_count = Field()
    read_complete_count = Field()
    read_progress_count = Field()
    total_score = Field()
    binding = Field()
    isbn13 = Field()
    isbn10 = Field()
    pub_version = Field()
