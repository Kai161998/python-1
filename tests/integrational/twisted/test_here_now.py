from twisted.internet import defer
from twisted.internet.task import deferLater
from twisted.internet.tcp import Client
from twisted.internet import reactor
from twisted.trial import unittest
from twisted.web.client import HTTPConnectionPool

import logging
import pubnub
from pubnub.pubnub_twisted import PubNubTwisted
from tests.helper import pnconf

pubnub.set_stream_logger('pubnub', logging.DEBUG)


class TestPubNubAsyncAsyncHereNow(unittest.TestCase):
    def setUp(self):
            self.pool = HTTPConnectionPool(reactor, False)

    def tearDown(self):
        def _check_fds(_):
            fds = set(reactor.getReaders() + reactor.getReaders())
            if not [fd for fd in fds if isinstance(fd, Client)]:
                return
            return deferLater(reactor, 0, _check_fds, None)

        return self.pool.closeCachedConnections().addBoth(_check_fds)

    def success(self, res):
        pass
        # self.assertEqual(res.total_occupancy, 1)

    def error(self, error):
        return defer.fail(error)

    def test_success_deferred(self):
        d = defer.Deferred()

        pubnub = PubNubTwisted(pnconf, reactor=reactor, pool=self.pool)

        pubnub.here_now() \
            .channels(["ch1", "ch2", "ch3", "demo"]) \
            .include_state(False) \
            .deferred() \
            .addCallback(self.success) \
            .addCallbacks(d.callback, d.errback)

        return d

    def test_success_sync(self):
        pubnub = PubNubTwisted(pnconf, reactor=reactor, pool=self.pool)

        res = pubnub.here_now() \
            .channels(["ch1", "ch2", "ch3", "demo"]) \
            .include_state(False) \
            .sync()

        print('sync', res)

    def xtest_success_async(self):
        d = defer.Deferred()

        pubnub = PubNubTwisted(pnconf, reactor=reactor, pool=self.pool)

        success = self.success
        error = self.error

        def success_wrapper(res):
            success(res)
            # REVIEW: Hanging on assertion
            d.callback(None)

        def error_wrapper(err):
            error(err)
            d.errback(None)

        pubnub.here_now() \
            .channels(["ch1", "ch2", "ch3", "demo"]) \
            .include_state(False) \
            .async(success_wrapper, error_wrapper)

        return d

