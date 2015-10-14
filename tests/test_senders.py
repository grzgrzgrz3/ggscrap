import unittest
from mock import patch, call
import senders


class TestBaseSender(unittest.TestCase):

    def setUp(self):
        self.openurl_patcher = patch('senders.OpenUrlWrapper')
        self.openurl = self.openurl_patcher.start()

        self.send_patcher = patch('senders.BaseSender.send')
        self.send = self.send_patcher.start()
        self.send.return_value = senders.ResponseSignals.SUCCESS

        self.sender = senders.BaseSender()

        self.example_req = {"paragony": [1234, 54321, 128], 'email': 'test_email@dupa.pl'}

    def tearDown(self):
        self.openurl_patcher.stop()
        self.send_patcher.stop()

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


class TestSendArgsDecorator(unittest.TestCase):

    def test_call_decorated_function(self):
        mutable_object = []

        def func():
            mutable_object.append(1)

        senders.send_args(func)()
        self.assertTrue(mutable_object)

    def test_raise_when_wrapped_function_has_kwargs(self):
        self.assertRaises(TypeError, senders.send_args, lambda args1, arg2, kwargs1='saf': 0)

    def test_pass_only_necessary_args_in_correct_order(self):
        @senders.send_args
        def func(paragon, email, numer):
            return paragon, email, numer
        kwargs = {'paragon': 123, 'email': 'test@mail.com', 'numer': 7337, 'dummy_arg': 'dummy'}
        self.assertEquals(func(**kwargs), (123, 'test@mail.com', 7337))

    def test_passed_not_enought_arguments(self):
        @senders.send_args
        def func(paragon, email, numer, too_many1, too_many2):
            return paragon, email, numer, too_many1, too_many2

        kwargs = {'paragon': 123, 'email': 'test@mail.com', 'numer': 7337, 'dummy_arg': 'dummy'}
        self.assertRaises(TypeError, func, **kwargs)

if __name__ == '__main__':
    unittest.main()
