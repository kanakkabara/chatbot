import scrapy


class FinancecrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    keywords = scrapy.Field()
    body = scrapy.Field()

