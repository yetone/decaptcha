import tempfile

import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    handle_httpstatus_list = [500]

    def start_requests(self):
        yield self.fake_request(True)
        for i in range(20):
            yield self.fake_request(False)

    def fake_request(self, has_captcha):
        _, path = tempfile.mkstemp()
        url = 'file://' + path
        return scrapy.Request(url, meta={'has_captcha': has_captcha})

    def parse(self, response):
        print 'RESPONSE', response.body
