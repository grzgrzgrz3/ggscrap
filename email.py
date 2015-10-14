import re
from exception import DiscoverPop3Fail, EmailSyntaxError

DEFAULT_POP3_PORT = 995
POP3_SERVERS = (("^interia.[eu|pl]$", "poczta.interia.pl"),
                ("^poczta.fm$", "www.poczta.fm"),
                ("^wp.pl$", "pop3.wp.pl"))





 class EmailPop3(object):

    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password



    def _pop3_discovery(self):
        domain_pattern = r".+@(.*?)"
        domain_match = re.match(domain_pattern, self.email)
        if not domain_match:
            raise EmailSyntaxError("Email ({0}) is not correct email".format(self.email))
        domain = domain_match.group(1)

        for pattern, pop3_address in POP3_SERVERS:
            if re.match(pattern, domain):
                return pop3_address
        raise DiscoverPop3Fail("Can't find POP3 server details for email {0}".format(self.email))

    @property
    def _address(self):
        return self._pop3_discovery()

