from urlparse import urljoin

import scrapy
from twisted.internet.defer import inlineCallbacks

from decaptcha.exceptions import DecaptchaError
from decaptcha.utils.download import download


class RecaptchaEngine(object):

    CAPTCHA_XPATH = '//iframe[contains(@src, "google.com/recaptcha/api")]/@src'

    def __init__(self, crawler):
        self.crawler = crawler

    def has_captcha(self, response, **kwargs):
        sel = scrapy.Selector(response)
        return len(sel.xpath(self.CAPTCHA_XPATH)) > 0

    @inlineCallbacks
    def handle_captcha(self, response, solver):
        sel = scrapy.Selector(response)
        iframe_src = sel.xpath(self.CAPTCHA_XPATH).extract()[0]
        iframe_url = urljoin(response.url, iframe_src)
        iframe_request = scrapy.Request(iframe_url)
        iframe_response = yield download(self.crawler, iframe_request)
        iframe_sel = scrapy.Selector(iframe_response)
        img_src, = iframe_sel.xpath('//img/@src').extract()[:1] or [None]
        if img_src is None:
            raise DecaptchaError('No //img/@src found on CAPTCHA page')
        img_url = urljoin(iframe_response.url, img_src)
        img_request = scrapy.Request(img_url)
        img_response = yield download(self.crawler, img_request)
        scrapy.log.msg('CAPTCHA image downloaded, solving')
        captcha_text = yield solver.solve(img_response.body)
        scrapy.log.msg('CAPTCHA solved: %s' % captcha_text)
        challenge_request = scrapy.FormRequest.from_response(
            iframe_response, formxpath='//form',
            formdata={'recaptcha_response_field': captcha_text}
        )
        challenge_response = yield download(self.crawler, challenge_request)
        challenge_sel = scrapy.Selector(challenge_response)
        challenge, = challenge_sel.xpath(
            '//textarea/text()'
        ).extract()[:1] or [None]
        if not challenge:
            raise DecaptchaError('Bad challenge from reCAPTCHA API:\n%s' %
                                 challenge_response.body)
        scrapy.log.msg('CAPTCHA solved, submitting challenge')
        submit_request = scrapy.FormRequest.from_response(
            response, formxpath='//form[.%s]' % self.CAPTCHA_XPATH,
            formdata={'recaptcha_challenge_field': challenge}
        )
        yield download(self.crawler, submit_request)
