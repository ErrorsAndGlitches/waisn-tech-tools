import requests
from django.conf import settings
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from .get_twilio_cred import get_twilio_cred


class Messenger(object):
    def __init__(self):
        self.client = get_twilio_cred()

    def send(self, subscriber, filenames):
        message_to = subscriber.phone_number
        for filename in filenames:
            messageReply = Message(filename)
            messageReply = messageReply.contents()
            message = self.client.messages.create(
                body=messageReply,
                from_=settings.TWILIO_SMS_NUMBER,
                to=message_to
            )


class Message(object):
    def __init__(self, filename):
        self._filename = filename

    def contents(self):
        with open(self._filename) as f:
            messageReply = f.read()
            return messageReply
