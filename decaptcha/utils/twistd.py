from twisted.internet import reactor
from twisted.internet.defer import Deferred


def sleep(seconds):
    d = Deferred()
    reactor.callLater(seconds, d.callback, None)
    return d
