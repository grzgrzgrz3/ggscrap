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

    def _register_send(self, status=1, dane=None, paragony=None, additionals=None):
        dane = dane if dane else {}
        paragony = paragony if paragony else []
        additionals = additionals if additionals else {'ip': 1, 'ip_msg': 'done'}
        info = {'status': status, 'dane': dane, 'paragony': paragony}
        info.update(additionals)
        self.send_mock.return_value = str(info)

    def test_call_send_with_correct_args(self):
        self._register_send()
        self.control.new()
        self.send_mock.assert_called_once_with(["nowa_sesja", "testsender"])

    @patch('base.Control._log_new_action')
    def test_skip_on_used_ip(self, called_not_skipped):
        self._register_send(status=0, additionals={'ip': 0, 'ip_msg': 'ip_error_message'})
        self.control.new()
        called_not_skipped.assert_not_called()

    @patch('base.Control._log_new_action')
    def test_continue_on_true_status(self, called_not_skipper):
        self._register_send()
        self.control.new()
        self.assertEquals(called_not_skipper.call_count, 1)

    def test_call_sender_wiht_all_argumens(self):
        self._register_send(dane={'email': 'test@email.com', 'numer': 883042111},
                            paragony=[{'numer': 8321, 'data': '2015-03-12'}])
        self.control.new()
        self.sender().new_request.assert_called_once_with(email='test@email.com', numer=883042111,
                                                   paragony=[{'numer': 8321, 'data': '2015-03-12'}])

class TestBaseSender(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass



if __name__ == '__main__':
    unittest.main()