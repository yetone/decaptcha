from urlparse import parse_qsl
from uuid import uuid4
from io import BytesIO

import scrapy


class MultipartRequest(scrapy.FormRequest):

    def __init__(self, *args, **kwargs):
        super(MultipartRequest, self).__init__(*args, **kwargs)
        fields = parse_qsl(self._get_body())
        boundary = uuid4().hex
        body = BytesIO()

        for field, value in fields:
            body.write('--%s\r\n' % (boundary))
            body.write('Content-Disposition: form-data; name="%s"' %
                       field)
            body.write(b'\r\n\r\n')
            if isinstance(value, int):
                value = str(value)
            body.write(value)
            body.write(b'\r\n')
        body.write('--%s--\r\n' % (boundary))
        self._set_body(body.getvalue())

        self.headers['Content-Type'] = str(
            'multipart/form-data; boundary=%s' % boundary
        )

if __name__ == '__main__':
    r = MultipartRequest('http://api.dbcapi.me/api/captcha', formdata={'username': 'shirk3y', 'password': 'scraping2014'})
    print r._body

'''
{'Content-Length': '360', 'Content-Type': 'multipart/form-data; boundary=c8d36abc3a1c4d2e8ea5b5ade3004972'}
--c8d36abc3a1c4d2e8ea5b5ade3004972
Content-Disposition: form-data; name="username"

shirk3y
--c8d36abc3a1c4d2e8ea5b5ade3004972
Content-Disposition: form-data; name="password"

scraping2014
--c8d36abc3a1c4d2e8ea5b5ade3004972
Content-Disposition: form-data; name="captchafile"; filename="example_captcha2.gif"


--c8d36abc3a1c4d2e8ea5b5ade3004972--
'''