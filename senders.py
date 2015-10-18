import inspect
from base import OpenUrlWrapper


class BaseSender(object):
    _log = None

    def __init__(self):
        self._browser = OpenUrlWrapper()

    def new_request(self, **kwargs):
        self._browser.rebuild()
        paragony = kwargs.pop('paragony')
        for paragon in paragony:
            self.send(paragon=paragon, **kwargs)
        self.cleanup()

    @property
    def p(self):
        """
        Hack to provide backward compatibility
        """
        return self._browser

    def send(self, *args, **kwargs):
        raise NotImplemented()

    def _get_cases(self):
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

