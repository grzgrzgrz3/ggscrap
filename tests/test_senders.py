import unittest
from contextlib import contextmanager

from mock import patch, call, PropertyMock, MagicMock
from exception import MissingMethod, UnknownResponse
from senders import ALL_ACTION_METHODS, BaseSender, ResponseSignals, send_args, ResponseMatchSender


class SenderTest(unittest.TestCase):
    _all_action_methods = ALL_ACTION_METHODS

    def setUp(self):
        self.openurl_patcher = patch('senders.OpenUrlWrapper')
        self.openurl = self.openurl_patcher.start()

        self.send_patcher = patch('senders.BaseSender.send')
        self.send = self.send_patcher.start()
        self.send.return_value = ResponseSignals.SUCCESS

        self.sender = BaseSender()

        self.example_req = {"paragony": [1234, 54321, 128],
                            'email': 'test_email@dupa.pl'}

    @contextmanager
    def _mock_action_methods(self, methods, **kwargs):
        method_mocks = {}
        method_patchers = []
        for method in methods:
            effects = kwargs.get(method, [])
            method_patch = patch('senders.BaseSender.{0}'.format(method))
            method_mock = method_patch.start()
            if effects:
                method_mock.side_effect = effects
            else:
                method_mock.return_value = ResponseSignals.SUCCESS
            method_mocks.update({method: method_mock})
            method_patchers.append(method_patch)
        try:
            yield method_mocks
        finally:
            for patcher in method_patchers:
                patcher.stop()

    def tearDown(self):
        self.openurl_patcher.stop()
        self.send_patcher.stop()


class TestBaseSender(SenderTest):

    def test_send_need_to_be_overridden(self):
        self.send_patcher.stop()
        self.assertRaises(NotImplementedError,
                          self.sender.new_request, **self.example_req)
        self.send_patcher.start()

    def test_new_request_rebuild_browser(self):
        self.sender.new_request(**self.example_req)
        self.openurl().rebuild.assert_called_once_with()

    def test_send_called_count(self):
        self.sender.new_request(**self.example_req)
        self.assertEquals(self.send.call_count, len(self.example_req['paragony']))

    def test_send_called_with_correctA_args(self):
        self.sender.new_request(**self.example_req)
        correct_call_args_list = [call(email='test_email@dupa.pl', paragon=1234),
                                  call(email='test_email@dupa.pl', paragon=54321),
                                  call(email='test_email@dupa.pl', paragon=128)]
        self.assertEquals(self.send.call_args_list, correct_call_args_list)

    def test_signal_calls_signal(self):
        cases = [{'calls': (('send', 4*3),
                            ('pre_request', 1),
                            ('pre_send', 3),
                            ('clean', 3),
                            ('after_requests', 1)),
                  'site_effect': {'send': ([ResponseSignals.RESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  },
                 {'calls': (('send', 3),
                            ('pre_request', 4),
                            ('pre_send', 3),
                            ('clean', 3),
                            ('after_requests', 1)),
                  'site_effect': {'pre_request': ([ResponseSignals.RESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  },
                 {'calls': (('send', 3),
                            ('pre_request', 1),
                            ('pre_send', 3*4),
                            ('clean', 3),
                            ('after_requests', 1)),
                  'site_effect': {'pre_send': ([ResponseSignals.RESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  },
                 {'calls': (('send', 3),
                            ('pre_request', 1),
                            ('pre_send', 3),
                            ('clean', 3*4),
                            ('after_requests', 1)),
                  'site_effect': {'clean': ([ResponseSignals.RESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  },
                 {'calls': (('send', 3),
                            ('pre_request', 1),
                            ('pre_send', 3),
                            ('clean', 3),
                            ('after_requests', 4)),
                  'site_effect': {'after_requests': ([ResponseSignals.RESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  },
                 {'calls': (('send', 3*4),
                            ('pre_request', 1),
                            ('pre_send', 3*4),
                            ('clean', 3),
                            ('after_requests', 1)),
                  'site_effect': {'send': ([ResponseSignals.FULLRESEND]*3 + [ResponseSignals.SUCCESS])*3}
                  }]
        for test_number, case in enumerate(cases):
            with self._mock_action_methods(self._all_action_methods, **case['site_effect']) as mocks:
                self.sender.new_request(**self.example_req)
                for method, correct_call in case['calls']:
                    calls = mocks.pop(method).call_count
                    self.assertEqual(calls, correct_call,
                                     msg="({3}) {0} wrong calls. called:{1} != expected:{2}".format(
                                         method, calls, correct_call, test_number))


class TestResponseMatchSender(SenderTest):

    def setUp(self):
        super(TestResponseMatchSender, self).setUp()
        self.pattern_patcher = patch('senders.ResponseMatchSender.PATTERN_METHOD',
                                     create=True, new_callable=PropertyMock)
        self.pattern = self.pattern_patcher.start()

        self.pattern.return_value = r"^some response$"
        self.method_patcher = patch('senders.ResponseMatchSender.RESULT_METHOD',
                                    create=True)
        self.method = self.method_patcher.start()

    def tearDown(self):
        super(TestResponseMatchSender, self).tearDown()
        self.pattern_patcher.stop()
        self.method_patcher.stop()

    def test_raise_on_missing_response_method(self):
        self.method_patcher.stop()
        self.assertRaises(MissingMethod, ResponseMatchSender)
        self.method_patcher.start()

    def test_call_correct_method(self):
        self.send.return_value = "some response"
        ResponseMatchSender().new_request(**self.example_req)
        self.assertEqual(self.method.call_count, 3)

    def test_ignore_methods_not_responsable(self):
        with patch("senders.ResponseMatchSender.send",
                   return_value="some response") as send:
            del send.responsable
            ResponseMatchSender().new_request(**self.example_req)
            self.method.assert_not_called()
            send.responsable = False
            ResponseMatchSender().new_request(**self.example_req)
            self.method.assert_not_called()

    def test_raise_when_not_match(self):
        self.send.return_value = "not matchable response"
        with self.assertRaises(UnknownResponse):
            ResponseMatchSender().new_request(**self.example_req)

    def test_response_and_resend_cooperate(self):
        self.send.return_value = "some response"
        self.method.side_effect = ([ResponseSignals.RESEND]*3 + [1])*3
        ResponseMatchSender().new_request(**self.example_req)
        self.assertEqual(self.send.call_count, 3*4)


class TestSendArgsDecorator(unittest.TestCase):

    def test_call_decorated_function(self):
        mutable_object = []

        def func():
            mutable_object.append(1)

        send_args(func)(self)
        self.assertTrue(mutable_object)

    def test_raise_when_wrapped_function_has_kwargs(self):
        self.assertRaises(TypeError, send_args,
                          lambda args1, arg2, kwargs1='saf': 0)

    def test_pass_only_necessary_args_in_correct_order(self):
        @send_args
        def func(self, paragon, email, numer):
            return paragon, email, numer
        kwargs = {'paragon': 123, 'email': 'test@mail.com',
                  'numer': 7337, 'dummy_arg': 'dummy'}
        self.assertEquals(func(self=self, **kwargs),
                          (123, 'test@mail.com', 7337))

    def test_passed_not_enough_arguments(self):
        @send_args
        def func(self, paragon, email, numer, too_many1, too_many2):
            return paragon, email, numer, too_many1, too_many2

        kwargs = {'paragon': 123, 'email': 'test@mail.com',
                  'numer': 7337, 'dummy_arg': 'dummy'}
        with self.assertRaises(TypeError) as cm:
            func(self, **kwargs)
        self.assertEqual(str(cm.exception),
                         'Function func() require arguments: too_many1, too_many2')


if __name__ == '__main__':
    unittest.main()
