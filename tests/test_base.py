import unittest
import base
from mock import patch, MagicMock


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
        self.send_mock.assert_called_once_with(['nowa_sesja', "testsender"])

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

    @patch("base.OpenUrlWrapper.otworz")
    def test_wrapper_call_own_methods(self, wrapper_method):
        wrapper = base.OpenUrlWrapper(object)
        wrapper.otworz()
        wrapper_method.assert_called_once_with()

    def test_wrapper_redirect_calls_to_wrapped(self):
        wrapped = MagicMock()
        wrapper = base.OpenUrlWrapper(wrapped)
        wrapper.test_method()
        wrapped.test_method.called_once_with()


class TestBaseSender(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestResponse(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
