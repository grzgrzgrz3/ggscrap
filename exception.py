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
