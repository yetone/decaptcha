import json
from base64 import b64encode

import scrapy
from twisted.internet.defer import inlineCallbacks, returnValue

from decaptcha.exceptions import CaptchaIncorrectlySolved, CaptchaSolveTimeout
from decaptcha.utils.download import download


class DeathbycaptchaSolver(object):

    def __init__(self, crawler):
        self.crawler = crawler
        settings = crawler.settings
        self.username = settings.get('DECAPTCHA_DEATHBYCAPTCHA_USERNAME')
        self.password = settings.get('DECAPTCHA_DEATHBYCAPTCHA_PASSWORD')
        self.poll_times = settings.getint(
            'DECAPTCHA_DEATHBYCAPTCHA_POLL_TIMES', 60
        )
        self.poll_delay = settings.getfloat(
            'DECAPTCHA_DEATHBYCAPTCHA_POLL_DELAY', 2
        )
        self.api_url = 'http://api.dbcapi.me/api/captcha'

    @inlineCallbacks
    def solve(self, captcha_image):
        formdata = {
            'username': self.username,
            'password': self.password,
            'captchafile': 'base64:' + b64encode(captcha_image)
        }
        request = scrapy.FormRequest(self.api_url, formdata=formdata)
        response = yield download(self.crawler, request)
        # Redirecting must be enabled
        poll_url = response.url
        for retry in xrange(self.poll_times):
            poll_request = scrapy.Request(poll_url, dont_filter=True,
                                          headers={'Accept': 'application/json'})
            poll_response = yield download(self.crawler, poll_request)
            poll_data = json.loads(poll_response.body)
            if poll_data['is_correct'] is False:
                raise CaptchaIncorrectlySolved('Deathbycaptcha returned '
                                               'is_correct=false')
            if poll_data['text']:
                returnValue(poll_data['text'])
        raise CaptchaSolveTimeout('Deathbycaptcha did not solve CAPTCHA '
                                  'in time')
