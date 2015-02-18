BOT_NAME = 'decaptcha_example'

SPIDER_MODULES = ['decaptcha_example.spiders']
NEWSPIDER_MODULE = 'decaptcha_example.spiders'

DOWNLOADER_MIDDLEWARES = {
    'decaptcha.downloadermiddleware.decaptcha.DecaptchaMiddleware': 500,
}

DECAPTCHA_ENABLED = 1

DECAPTCHA_SOLVER = 'decaptcha.solvers.deathbycaptcha.DeathbycaptchaSolver'
DECAPTCHA_DEATHBYCAPTCHA_USERNAME = 'shirk3y'
DECAPTCHA_DEATHBYCAPTCHA_PASSWORD = 'scraping2014'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2148.0 Safari/537.36'