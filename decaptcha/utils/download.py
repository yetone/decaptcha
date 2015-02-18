def download(crawler, request):
    request.meta['captcha_request'] = True
    request.meta['dont_cache'] = True
    return crawler.engine.download(request, crawler.spider)
