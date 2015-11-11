class ConfigError(Exception):
    pass


class UnrecognizedIpchangeType(ConfigError):
    pass


class EmailException(Exception):
    pass


class EmailSyntaxError(EmailException):
    pass


class DiscoverPop3Fail(EmailException):
    pass


class EmailFetchError(EmailException):
    pass


class EmailWaitTimeout(EmailException):
    pass


class MissingMethod(Exception):
    pass


class UnknownResponse(Exception):
    def __init__(self, method):
        method_name = getattr(method, __name__)
        msg = "Do not match response for method {0}".format(method_name)
        super(UnknownResponse, self).__init__(msg)