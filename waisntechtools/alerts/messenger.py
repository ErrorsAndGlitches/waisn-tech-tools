from django.conf import settings

from alerts.twilio import TwilioClientFactory


class Messenger(object):
    def __init__(self, client=TwilioClientFactory.new_client()):
        self.client = client

    def send(self, subscriber, filenames):
        message_to = subscriber.phone_number
        for file in filenames:
            self.client.messages.create(
                body=Message(file).contents(),
                from_=settings.TWILIO_SMS_NUMBER,
                to=message_to
            )


class Message(object):
    def __init__(self, file):
        self._file = file

    def contents(self):
        with open(self._file) as f:
            return f.read()
