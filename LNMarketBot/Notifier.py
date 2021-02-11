import logging
from notifiers import get_notifier
from notifiers.logging import NotificationHandler
from collections import namedtuple


class Notifier:

    def __init__(self, silent=False):
        self.telegram = None
        self.pushover = None
        self.stdout = False
        self.silent = silent

    def enableStdout(self):
        self.stdout = True

    def enableTelegram(self, chatID, token):
        self.telegram = namedtuple('Telegram', 'notifier chatID token')(
            get_notifier('telegram'),
            chatID,
            token,
            )

        defaults = {
            'chat_id': chatID,
            'token': token,
            }
        handler = NotificationHandler('telegram', defaults=defaults)
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        log = logging.getLogger()
        log.addHandler(handler)
        self.notify('Telegram enabled for logging')

    def enablePushover(self, userkey, APIkey):
        self.pushover = namedtuple('Pushover', 'notifier APIkey userkey')(
            get_notifier('pushover'),
            APIkey,
            userkey,
            )

        defaults = {
            'user': userkey,
            'token': APIkey,
            }
        handler = NotificationHandler('pushover', defaults=defaults)
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        log = logging.getLogger()
        log.addHandler(handler)
        self.notify('Pushover enabled for logging')

    def notify(self, message):
        if self.stdout:
            print(message)
        if self.telegram is not None:
            self.telegram.notifier.notify(
                token=self.telegram.token,
                chat_id=self.telegram.chatID,
                message=message,
            )
        if self.pushover is not None:
            self.pushover.notifier.notify(
                token=self.pushover.APIkey,
                user=self.pushover.userkey,
                message=message,
            )


def addMessage(f):
    def Wrapper(self, *args, **kwargs):
        message = f'Calling {f.__name__}('
        if args:
            message += ','.join([str(e) for e in args]) + ','
        if kwargs:
            message += str(kwargs)[1:-1]
        message += ')'
        if not self.notifier.silent:
            self.notifier.notify(message)
        return f(self, *args, **kwargs)
    return Wrapper
