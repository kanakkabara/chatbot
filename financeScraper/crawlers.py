from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
import fileinput
from datetime import datetime

from financeScraper.financeScraper.items import FinancescraperItem
from financeScraper.financeScraper import settings as my_settings

import financeScraper.financeScraper.utils as utils

import scrapy


"""
    Class: MWSpider
    Description: Spider for crawling MarketWatch links given a stock
    ticker symbol and its own articles.
"""
class MWSpider(scrapy.Spider):
    home       = 'https://marketwatch.com'
    name       = "mws"

    def create_start_url(self, tick):
        return "".join(["https://www.marketwatch.com/investing/stock/", tick, "/news"])

    def __init__(self, *args, **kwargs):
        super(MWSpider, self).__init__(*args, **kwargs)
        self.tick = kwargs.get('tick')
        self.start_urls = [self.create_start_url(self.tick)]


    def parse(self, response):
        for article in response.xpath('//li/div/p/a'):
            article_link = article.xpath('@href').extract_first()
            yield response.follow(article_link, callback=self.parse_article) if article_link is not None else ""

    def parse_article(self, response):
        yield utils.parse(response, self.tick)

"""
    Class: ReutersSpider
"""
class ReutersSpider(scrapy.Spider):

    home = 'https://www.reuters.com'
    name = 'reu'

    def create_start_url(self, tick):
        return "".join(["https://www.reuters.com/finance/stocks/company-news/", tick, ".OQ"])

    def __init__(self, *args, **kwargs):
        super(ReutersSpider, self).__init__(*args, **kwargs)
        self.tick = kwargs.get('tick')
        self.start_urls = [self.create_start_url(self.tick)]

    def parse(self, response):
        for article in response.xpath('//div[@class=\'feature\']'):

            article_link = article.xpath('h2/a/@href').extract_first()
            article_link = "".join([self.home, article_link])
            yield response.follow(article_link, callback=self.parse_article) if article_link is not None else ""

    def parse_article(self, response):
        yield utils.parse(response, self.tick)

"""
    Class: WSJSpider
    Description: Spider for Wall Street Journal. Currently WIP to
    obtain more relevant article links. Does not scrap articles.
"""
class WSJSpider(scrapy.Spider):

    home = 'https://www.wsj.com'
    name = 'wsj'

    def __init__(self, *args, **kwargs):
        super(WSJSpider, self).__init__(*args, **kwargs)
        self.tick = kwargs.get('tick')
        self.start_urls = [self.create_start_url(self.tick)]

    def parse(self, response):
        for article in response.xpath(
                '//ul[@class=\'cr_newsSummary\']//span[@class=\'headline\']'
            ):

            article_link = article.xpath('a/@href').extract_first()
            yield response.follow(article_link, callback=self.parse_article) if article_link is not None else ""

    """
    TODO: Subscriber/Login Wall...
    """
    def parse_article(self, response):
        return

"""
    Class: BloSpider
"""
class BloSpider(scrapy.Spider):
    home       = 'https://marketwatch.com'
    name       = "blo"

    def create_start_url(self, tick):
        return "".join(["https://www.bloomberg.com/quote/", tick, ":US"])

    def __init__(self, *args, **kwargs):
        super(BloSpider, self).__init__(*args, **kwargs)
        self.tick = kwargs.get('tick')
        self.start_urls = [self.create_start_url(self.tick)]


    def parse(self, response):
        for article in response.xpath('//article[@class]'):
            article_link = article.xpath('a/@href').extract_first()
            yield response.follow(article_link, callback=self.parse_article) if article_link is not None else ""

    def parse_article(self, response):
        yield utils.parse(response, self.tick)


def read_file(fn):
    with open(fn, 'r') as f:
        for ticker in f.readlines():
            yield ticker.strip()

"""
    Class: MSNBCSpider
"""
class MSNBCSpider(scrapy.Spider):
    home       = 'https://www.cnbc.com'
    name       = "msn"

    def create_start_url(self, tick):
        return "".join(["https://www.cnbc.com/quotes/?symbol=", tick, "&tab=news"])

    def __init__(self, *args, **kwargs):
        super(MSNBCSpider, self).__init__(*args, **kwargs)
        self.tick = kwargs.get('tick')
        self.start_urls = [self.create_start_url(self.tick)]

    def parse(self, response):
        for article in response.xpath('//div[@class=\"assets\"]/a'):
            article_link = article.xpath('@href').extract_first()
            yield response.follow(article_link, callback=self.parse_article) if article_link is not None else ""

    def parse_article(self, response):
        yield utils.parse(response, self.tick)


def crawl(ticks):
    # Create and run spiders
    try:
        stocks_checked = []
        today_date = datetime.now()
        datetime_format_string = '%b-%d-%Y'
        with fileinput.input(files=('stocks.txt'), inplace=True, backup='.bak') as f:
            for line in f:
                ticker, date = line.rstrip().split(",")
                if any(ticker in tick for tick in ticks):
                    stocks_checked.append(ticker)
                    date_crawled = datetime.strptime(date, datetime_format_string)
                    last_crawled = (today_date - date_crawled).days
                    if last_crawled < 2:
                        ticks.remove(ticker)
                        print(line.rstrip())
                    else:
                        print(ticker+","+today_date.strftime(datetime_format_string))
                else:
                    print(line.rstrip())

        for tick in ticks:
            if not any(tick in stock for stock in stocks_checked):
                with open("stocks.txt", "a") as stocks_file:
                    stocks_file.write(tick+","+today_date.strftime(datetime_format_string))

        configure_logging()
        crawler_settings = Settings()
        crawler_settings.setmodule(my_settings)
        runner = CrawlerRunner(settings=crawler_settings)
        if ticks:
            for tick in ticks:
                kwargs = {'tick': tick}
                runner.crawl(ReutersSpider, **kwargs)
                runner.crawl(BloSpider, **kwargs)

            d = runner.join()
            d.addBoth(lambda _: reactor.stop())
            reactor.run()
    except IOError:
        print("I/O error")

def main():
    crawl(["MSFT"])

if __name__ == '__main__':
    main()
