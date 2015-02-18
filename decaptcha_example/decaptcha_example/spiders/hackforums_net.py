import scrapy


class HackforumsNetSpider(scrapy.Spider):
    name = 'hackforums.net'
    start_urls = ['http://hackforums.net']
    handle_httpstatus_list = [403]

    def parse(self, response):
        pass
