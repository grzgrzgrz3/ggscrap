import unittest
import base
from mock import patch, MagicMock
from exception import UnrecognizedIpchangeType
import logging

logging.disable(logging.CRITICAL)


class TestControl(unittest.TestCase):

    def setUp(self):
        self.send_patcher = patch('base.send')
        self.send_mock = self.send_patcher.start()

        self.log_patcher = patch('base.log')
        self.log_mock = self.log_patcher.start()

        self.sender = MagicMock()
        self.sender().__class__.__name__ = 'TestSender'

        # ipchange mocks
        self.zmiana_patcher = patch("base.zmiana")
        self.zmiana = self.zmiana_patcher.start()

        self.ipchange_patcher = patch("base.ipchange")
        self.ipchange = self.ipchange_patcher.start()

        self.config_patcher = patch("base.config")
        self.config = self.config_patcher.start()
        self.config.get.return_value = 'play'

        self.ip_patcher = patch("base.ip")
        self.ip = self.ip_patcher.start()

        self.control = base.Control(self.sender)

    def tearDown(self):
        self.send_patcher.stop()
        self.log_patcher.stop()
        self.ipchange_patcher.stop()
        self.zmiana_patcher.stop()
        self.config = self.config_patcher.stop()
        self.ip_patcher.stop()

    def _register_send(self, status=1, dane=None, paragony=None, additional=None):
        dane = dane if dane else {}
        paragony = paragony if paragony else []
        additional = additional if additional else {'ip': 1, 'ip_msg': 'done'}
        info = {'status': status, 'dane': dane, 'paragony': paragony}
        info.update(additional)
        self.send_mock.return_value = str(info)

    def test_call_send_with_correct_args(self):
        self._register_send()
        self.control.new_request()
        self.send_mock.assert_called_once_with(["testsender", 'nowa_sesja'])

    @patch('base.Control._log_new_action')
    def test_skip_on_used_ip(self, called_not_skipped):
        self._register_send(status=0, additional={'ip': 0, 'ip_msg': 'ip_error_message'})
        self.control.new_request()
        called_not_skipped.assert_not_called()

    @patch('base.Control._log_new_action')
    def test_continue_on_true_status(self, called_not_skipper):
        self._register_send()
        self.control.new_request()
        self.assertEquals(called_not_skipper.call_count, 1)

    def test_call_sender_with_all_arguments(self):
        self._register_send(dane={'email': 'test@email.com', 'numer': 883042111},
                            paragony=[{'numer': 8321, 'data': '2015-03-12'}])
        self.control.new_request()
        self.sender().new_request.assert_called_once_with(email='test@email.com', numer=883042111,
                                                          paragony=[{'numer': 8321, 'data': '2015-03-12'}])

    def test_new_request_lock_and_free(self):
        self._register_send()
        self.control.new_request()
        self.ip().stop.assert_called_once_with()
        self.ip().start.assert_called_once_with()

    def test_new_request_change_ip_neo(self):
        self._register_send()
        self.config.get.return_value = 'neo'
        self.control.new_request()
        self.zmiana.assert_called_once_with()
        self.ipchange.assert_not_called()

    def test_new_request_change_ip_play(self):
        self._register_send()
        self.config.get.return_value = 'play'
        self.control.new_request()
        self.zmiana.assert_not_called()
        self.ipchange.assert_called_once_with()

    def test_new_request_raise_wrong_config(self):
        self._register_send()
        self.config.get.return_value = 'wrong_value'
        self.assertRaises(UnrecognizedIpchangeType, self.control.new_request)


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


class TestResponse(unittest.TestCase):

    def setUp(self):
        self.beatifulsoup_patch = patch("base.BeautifulSoup")
        self.beatifulsoup = self.beatifulsoup_patch.start()
        self.response = base.Response("")

    def tearDown(self):
        self.beatifulsoup_patch.stop()

    def test_soup_response(self):
        self.assertIsInstance(self.response.soup_response, self.beatifulsoup().__class__)

    def _create_input(self, name, value):
        input_mock = MagicMock()
        input_dict = {"name": name, 'value': value}
        input_mock.__getitem__.side_effect = input_dict.__getitem__
        input_mock.get.side_effect = input_dict.get
        return input_mock

    def test_inputs_get_return_correct_dict_with_inputs(self):
        form = MagicMock()
        inputs = [("accept", "yes"), ("rules", "on"), ("email", "")]
        form.findAll.return_value = [self._create_input(*args) for args in inputs]
        self.beatifulsoup().find.return_value = form

        self.assertEquals(self.response.inputs(), dict(inputs))

    @patch("__builtin__.open", create=True)
    def test_save_in_pretty_format(self, open_mock):
        fd_mock = MagicMock()
        open_mock.return_value = fd_mock
        name = "test_name"
        self.beatifulsoup().prettify.return_value = "pretty html"
        self.response.save(name)
        open_mock.assert_called_once_with("html/test_name.html", "wb")
        fd_mock.write.assert_called_once_with("pretty html")
        fd_mock.close.assert_called_once_with()



if __name__ == '__main__':
    unittest.main()
