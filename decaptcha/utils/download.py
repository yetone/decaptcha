def download(crawler, request):
    request.meta['captcha_request'] = True
    request.meta['dont_cache'] = True
    if hasattr(crawler, 'spider'):
        spider = crawler.spider
    else:
        spider = crawler.engine.spider
    return crawler.engine.download(request, spider)
