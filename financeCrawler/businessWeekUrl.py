import scrapy
import urllib


def businessWeekUrl():
    totalWeeks = []
    totalPosts = []
    url = 'http://www.businessweek.com/archive/news.html#r=404'
    data = urllib.urlopen(url).read()
    hxs = scrapy.Selector(text=data)

    months = hxs.xpath('//ul/li/a').re('http://www.businessweek.com/archive/\\d+-\\d+/news.html')
    admittMonths = 12 * (2013 - 2007) + 8
    months = months[:admittMonths]

    for month in months:
        data = urllib.urlopen(month).read()
        hxs = scrapy.Selector(text=data)
        weeks = hxs.xpath('//ul[@class="weeks"]/li/a').re(
            'http://www.businessweek.com/archive/\\d+-\\d+/news/day\\d+\.html')
        totalWeeks += weeks

    for week in totalWeeks:
        data = urllib.urlopen(week).read()
        hxs = scrapy.Selector(text=data)
        posts = hxs.xpath('//ul[@class="archive"]/li/h1/a/@href').extract()
        totalPosts += posts

    with open("businessweek.txt", "a") as myfile:
        for post in totalPosts:
            post = post + '\n'
            myfile.write(post)


businessWeekUrl()