import unittest
import base
from mock import patch, MagicMock, call


class TestControl(unittest.TestCase):

    def setUp(self):
        self.send_patcher = patch('base.send')
        self.send_mock = self.send_patcher.start()

        self.log_patcher = patch('base.log')
        self.log_mock = self.log_patcher.start()

        self.sender = MagicMock()
        self.sender().__class__.__name__ = 'TestSender'

        self.control = base.Control(self.sender)

    def tearDown(self):
        self.send_patcher.stop()
        self.log_patcher.stop()

    def _register_send(self, status=1, dane=None, paragony=None, additional=None):
        dane = dane if dane else {}
        paragony = paragony if paragony else []
        additional = additional if additional else {'ip': 1, 'ip_msg': 'done'}
        info = {'status': status, 'dane': dane, 'paragony': paragony}
        info.update(additional)
        self.send_mock.return_value = str(info)

    def test_call_send_with_correct_args(self):
        self._register_send()
        self.control.new()
        self.send_mock.assert_called_once_with(["testsender", 'nowa_sesja'])

    @patch('base.Control._log_new_action')
    def test_skip_on_used_ip(self, called_not_skipped):
        self._register_send(status=0, additional={'ip': 0, 'ip_msg': 'ip_error_message'})
        self.control.new()
        called_not_skipped.assert_not_called()

    @patch('base.Control._log_new_action')
    def test_continue_on_true_status(self, called_not_skipper):
        self._register_send()
        self.control.new()
        self.assertEquals(called_not_skipper.call_count, 1)

    def test_call_sender_with_all_arguments(self):
        self._register_send(dane={'email': 'test@email.com', 'numer': 883042111},
                            paragony=[{'numer': 8321, 'data': '2015-03-12'}])
        self.control.new()
        self.sender().new_request.assert_called_once_with(email='test@email.com', numer=883042111,
                                                          paragony=[{'numer': 8321, 'data': '2015-03-12'}])


class TestWrapper(unittest.TestCase):

    @patch("base.OpenUrlWrapper.open")
    def test_wrapper_call_own_methods(self, wrapper_method):
        wrapper = base.OpenUrlWrapper(object)
        wrapper.open()
        wrapper_method.assert_called_once_with()

    def test_wrapper_redirect_calls_to_wrapped(self):
        wrapped = MagicMock()
        wrapper = base.OpenUrlWrapper(wrapped)
        wrapper.test_method()
        wrapped.test_method.called_once_with()


class TestBaseSender(unittest.TestCase):

    def setUp(self):
        self.openurl_patcher = patch('base.OpenUrlWrapper')
        self.openurl = self.openurl_patcher.start()

        self.send_patcher = patch('base.BaseSender.send')
        self.send = self.send_patcher.start()

        self.sender = base.BaseSender()

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
        correcT_call_args_list = [call(email='test_email@dupa.pl', paragon=1234),
                                  call(email='test_email@dupa.pl', paragon=54321),
                                  call(email='test_email@dupa.pl', paragon=128)]
        self.assertEquals(self.send.call_args_list, correcT_call_args_list)

class TestResponse(unittest.TestCase):
    # TODO: write test for Response class
    pass


if __name__ == '__main__':
    unittest.main()
