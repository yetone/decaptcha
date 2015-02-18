from os.path import dirname, join


class ExampleEngine(object):

    def __init__(self, *args, **kwargs):
        pass

    def has_captcha(self, response, **kwargs):
        return response.meta.get('has_captcha', False)

    def get_captcha_image(self, *args, **kwargs):
        path = join(dirname(__file__), 'example_captcha.gif')
        return open(path).read()

    def submit_captcha(self, *args, **kwargs):
        pass
