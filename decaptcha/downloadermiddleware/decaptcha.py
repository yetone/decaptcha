"""Stub for implementing DeathByCaptcha service"""

from scrapy import log, signals
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
        self.paused = False
        self.queue = []
        if not self.enabled:
            raise NotConfigured('Please set DECAPTCHA_ENABLED to True')
        if not self.solver:
            raise NotConfigured('No valid DECAPTCHA_SOLVER provided')
        if not self.engines:
            raise NotConfigured('No valid DECAPTCHA_ENGINES provided')
        crawler.signals.connect(self.spider_idle,
                                signal=signals.spider_idle)

    def process_request(self, request, spider):
        if request.meta.get('captcha_request', False):
            return
        if self.paused:
            self.queue.append((request, spider))
            raise IgnoreRequest('Crawling paused, because CAPTCHA is '
                                'being solved')

    def process_response(self, request, response, spider):
        if request.meta.get('captcha_request', False):
            return response
        if self.paused:
            self.queue.append((request, spider))
            raise IgnoreRequest('Crawling paused, because CAPTCHA is '
                                'being solved')
        # A hack to have access to .meta attribute in engines and solvers
        response.request = request
        for engine in self.engines:
            if engine.has_captcha(response):
                log.msg('CAPTCHA detected, getting CAPTCHA image')
                self.pause_crawling()
                self.queue.append((request, spider))
                dfd = maybeDeferred(engine.handle_captcha,
                                    response=response, solver=self.solver)
                dfd.addCallback(self.captcha_handled)
                dfd.addErrback(self.captcha_handle_error)
                raise IgnoreRequest('Response ignored, because CAPTCHA '
                                    'was detected')
        return response

    def pause_crawling(self):
        self.paused = True

    def resume_crawling(self):
        self.paused = False
        for request, spider in self.queue:
            request.dont_filter = True
            self.crawler.engine.crawl(request, spider)
        self.queue[:] = []

    def spider_idle(self):
        self.resume_crawling()

    def captcha_handled(self, _):
        log.msg('CAPTCHA handled, resuming crawling')
        self.resume_crawling()

    def captcha_handle_error(self, failure):
        log.msg('CAPTCHA handle error: {}'.format(failure))
        self.resume_crawling()

    def _load_objects(self, classpaths):
        objs = []
        for classpath in classpaths:
            obj = load_object(classpath)(self.crawler)
            objs.append(obj)
        return objs
