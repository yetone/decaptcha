"""Stub for implementing DeathByCaptcha service"""

from scrapy import log
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.utils.misc import load_object
from twisted.internet.defer import maybeDeferred


class DecaptchaMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.engines = self._load_objects(
            self.settings.getlist('DECAPTCHA_ENGINES')
        )
        self.solver, = self._load_objects(
            self.settings.getlist('DECAPTCHA_SOLVER')
        )[:1] or [None]
        self.enabled = self.settings.getbool('DECAPTCHA_ENABLED')
        self.solving = False
        self.queue = []
        if not self.enabled:
            raise NotConfigured('Please set DECAPTCHA_ENABLED to True')
        if not self.solver:
            raise NotConfigured('No valid DECAPTCHA_SOLVER provided')
        if not self.engines:
            raise NotConfigured('No valid DECAPTCHA_ENGINES provided')

    def process_request(self, request, spider):
        if request.meta.get('captcha_request', False):
            return
        if self.solving:
            self.queue.append((request, spider))
            raise IgnoreRequest('Crawling paused, because CAPTCHA is '
                                'being solved')

    def process_response(self, request, response, spider):
        if request.meta.get('captcha_request', False):
            return response
        # A hack to have access to .meta attribute in engines and solvers
        response.request = request
        for engine in self.engines:
            if engine.has_captcha(response):
                log.msg('CAPTCHA detected, getting CAPTCHA image')
                self.solving = True
                self.queue.append((request, spider))
                dfd = maybeDeferred(engine.handle_captcha,
                                    response=response, solver=self.solver)
                dfd.addCallback(self.captcha_handled)
                raise IgnoreRequest('Response ignored, because CAPTCHA '
                                    'was detected')
        return response

    def captcha_handled(self, _):
        log.msg('CAPTCHA handled, resuming crawling')
        self.solving = False
        for request, spider in self.queue:
            request.dont_filter = True
            self.crawler.engine.crawl(request, spider)
        self.queue[:] = []

    def _load_objects(self, classpaths):
        objs = []
        for classpath in classpaths:
            obj = load_object(classpath)(self.crawler)
            objs.append(obj)
        return objs
