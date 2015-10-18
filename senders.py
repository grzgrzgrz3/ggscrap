import inspect
from base import OpenUrlWrapper


class ResponseSignals:
    SUCCESS = 1
    RESEND = 2
    CAPTCHA = RESEND
    FULLRESEND = 3


class BaseSender(object):
    _log = None

    def __init__(self):
        self._browser = OpenUrlWrapper()

    def new_request(self, **kwargs):
        self._browser.rebuild()
        self._resend_handle(self.pre_request)

        paragony = kwargs.pop('paragony')
        for paragon in paragony:
            while 1:
                res_signal = self._resend_handle(self._send_request,
                                                 signal=ResponseSignals.FULLRESEND,
                                                 paragon=paragon, **kwargs)
                self._resend_handle(self.clean)
                if res_signal == ResponseSignals.SUCCESS:
                    break

        self._resend_handle(self.after_requests)

    def _send_request(self, *args, **kwargs):
        self._resend_handle(self.pre_send)
        return self._resend_handle(self.send, *args, **kwargs)

    def _resend_handle(self, method, *args, **kwargs):
        signal = kwargs.pop('signal', ResponseSignals.RESEND)
        while 1:
            response = method(*args, **kwargs)
            if response == signal:
                continue
            return response

    @property
    def p(self):
        """
        Hack to provide backward compatibility
        """
        return self._browser

    def send(self, *args, **kwargs):
        raise NotImplemented()

    def pre_request(self, *args, **kwags):
        pass

    def pre_send(self, *args, **kwargs):
        pass

    def clean(self, *args, **kwargs):
        pass

    def after_clean(self, *args, **kwargs):
        pass

    def after_requests(self, *args, **kwargs):
        pass

    def cleanup(self, *args, **kwargs):
        pass


def send_args(func):
    args = inspect.getargspec(func)
    if args.defaults:
        raise TypeError("wrapped function {0}() can't have keyword arguments".format(func.__name__))

    def wrapper(self, **kwargs):
        kwargs.update({"self": self})
        test_args = list(args.args)
        map(test_args.remove, [arg for arg in kwargs.keys() if arg in test_args])
        if test_args:
            raise TypeError("Function {0}() require arguments: {1}".format(func.__name__, ", ".join(test_args)))

        arguments = (kwargs[arg] for arg in args.args)
        return func(*arguments)

    return wrapper
