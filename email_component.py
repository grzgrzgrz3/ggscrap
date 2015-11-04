# -*- coding: utf-8 -*-

import re
import time
import email
import poplib
from parse_mail import get_mail_contents, decode_text, getmailheader, getmailaddresses
from exception import DiscoverPop3Fail, EmailSyntaxError, EmailFetchError, EmailWaitTimeout

poplib._MAXLINE = 204800

DEFAULT_POP3_PORT = 995
POP3_SERVERS = ((r"^interia.(eu|pl)$", "poczta.interia.pl"),
                (r"^poczta.fm$", "www.poczta.fm"),
                (r"^wp.pl$", "pop3.wp.pl"))


class Email(object):

    def __init__(self, email_address, password):
        self.email = email_address
        self.password = password
        self._mail_box = MailBoxPop3(self.email, self.password)

    def clear(self):
        for message in self.emails():
            print "deleting: {0}".format(str(message))
            message.delete()
        self._mail_box.quit()

    def emails(self):
        return self._mail_box.fetch_emails()

    def find_pattern(self, pattern):
        start = time.time()
        for message in self._mail_box.get_new_messages(60*5):
            if re.match(pattern, message.body):
                result = re.match(pattern, message.body).group(1)
                print "Pattern found after: {0} seconds, result: {1}".format(round(time.time() - start),
                                                                     result)
                return result

    def test_fetch(self):
        for message in self._mail_box.get_new_messages(60*5):
            print message.title


class MailBoxPop3(object):
    _connection = None
    _list = None

    def __init__(self, email_address, password):
        self.email = email_address
        self.password = password

    def _pop3_discovery(self):
        domain_pattern = r".+@(.*?)$"
        domain_match = re.match(domain_pattern, self.email)
        if not domain_match:
            raise EmailSyntaxError("Email ({0}) is not correct email".format(self.email))
        domain = domain_match.group(1)
        for pattern, pop3_address in POP3_SERVERS:
            if re.match(pattern, domain):
                return pop3_address
        raise DiscoverPop3Fail("Can't find POP3 server details for email {0}".format(self.email))

    @property
    def address(self):
        return self._pop3_discovery()

    @property
    def _pop3_connection(self):
        if not self._connection:
            self._connection = RetryPop3(self)
        return self._connection

    def fetch_emails(self):
        self.clear_list_cache()
        for msg_id in self._msg_list:
            try:
                yield Message(msg_id, self)
            except EmailFetchError:
                print "Message probably corrupted"

    @property
    def _msg_list(self):
        if not self._list:
            self._list = self._get_list()
        return self._list

    def clear_list_cache(self):
        self._list = None

    def delete_message(self, msg):
        self._pop3_connection.dele(msg)

    def __del__(self):
        self.quit()

    def quit(self):
        if self._pop3_connection:
            self._pop3_connection.quit()

    def id_to_mailbox_number(self, msg_id):
        return self._msg_list[msg_id]

    def read_message(self, msg):
        try:
            message = "\r\n".join(self._pop3_connection.retr(msg)[1])
        except poplib.error_proto:
            raise
        return email.message_from_string(message)

    def get_new_messages(self, timeout=60):
        yielded = set()
        start = time.time()
        while start + timeout > time.time():
            msg_list = set(self._get_list().keys()).difference(yielded)
            for msg_id in msg_list:
                try:
                    yield Message(msg_id, self)
                    start = time.time()
                except EmailFetchError:
                    print "Message probably corrupted"
            yielded.update(msg_list)
            if not msg_list:
                time.sleep(10)
                self._pop3_connection.reconnect()
        raise EmailWaitTimeout("Do not get new message in {0} seconds".format(timeout))

    def _get_list(self):
        pop_list = self._pop3_connection.list()
        if pop_list[0].startswith('+OK'):
            msg_list = pop_list[1]
        else:
            raise
        return dict((int(msg.split(' ')[1]), int(msg.split(' ')[0])) for msg in msg_list)


class RetryPop3(object):
    _max_tries = 2
    _tried = 0
    _support_errors = ('-ERR',)
    _pop3_connection = None
    func = None

    def __init__(self, mail_box):
        self._mail_box = mail_box
        self._connect()

    def wrapper(self, func):
        def inside(*args, **kwargs):
            while 1:
                try:
                    args = self._process_msg_args(args)

                    result = getattr(self._pop3_connection, func)(*args, **kwargs)
                    self._tried = 0
                    return result
                except poplib.error_proto as e:
                    self._is_disconnected()
                    if e[0] in self._support_errors:
                        print id(self._pop3_connection)
                        if self._tried >= self._max_tries:
                            raise
                        print 'fetch error retry({0})'.format(self._tried)
                        self.reconnect(5)
                        self._tried += 1
                        continue
                    raise
        return inside

    def _process_msg_args(self, args):
        if args:
            if isinstance(args[0], Message):
                args = list(args)
                args[0] = self._mail_box.id_to_mailbox_number(args[0].number)
        return args

    def _is_disconnected(self):
        try:
            self._pop3_connection.noop()
            raise EmailFetchError()
        except:
            raise

    def quit(self):
        if hasattr(self._pop3_connection, 'file'):
            return self._pop3_connection.quit()

    def reconnect(self, sleep=0):
        self.quit()
        time.sleep(sleep)
        self._mail_box.clear_list_cache()
        self._connect()

    def _connect(self):
        self._pop3_connection = poplib.POP3(self._mail_box.address)
        self._pop3_connection.user(self._mail_box.email)
        self._pop3_connection.pass_(self._mail_box.password)

    def __getattr__(self, item):
        return self.wrapper(item)


class Message(object):
    _message = None

    def __init__(self, number, pop3):
        self.number = number
        self._pop3 = pop3
        self._prefetch()

    def _prefetch(self):
        self._message = self._pop3.read_message(self)

    @property
    def title(self):
        return getmailheader(self._message.get('Subject', '')).encode('utf-8')

    @property
    def sender(self):
        from_ = getmailaddresses(self._message, 'from')
        from_ = ('', '') if not from_ else from_[0]
        return from_

    @property
    def receiver(self):
        to = getmailaddresses(self._message, 'to')
        if to:
            return to[0][0]
        return ''

    @property
    def body(self):
        attachments = get_mail_contents(self._message)
        full_body = ""
        for attach in attachments:
            if attach.is_body:
                payload, used_charset = decode_text(attach.payload, attach.charset, 'auto')
                full_body += payload
        return full_body

    def delete(self):
        self._pop3.delete_message(self)

    def __str__(self):
        try:
            return "email: {0}, subject: {1}, sender: {2}, receiver: {3}".format(self.number, self.title,
                                                                                 self.sender, self.receiver)
        except UnicodeEncodeError:
            return "email: {0}, subject: {1}, sender: {2}, receiver: {3}".format(self.number, repr(self.title),
                                                                                 self.sender, repr(self.receiver))
