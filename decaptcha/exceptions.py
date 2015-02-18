class DecaptchaError(Exception):
    pass


class CaptchaIncorrectlySolved(DecaptchaError):
    pass


class CaptchaSolveTimeout(DecaptchaError):
    pass
