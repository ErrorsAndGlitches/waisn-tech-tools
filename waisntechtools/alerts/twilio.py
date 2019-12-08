from django.conf import settings
from twilio.rest import Client


class TwilioClientFactory(object):

    @staticmethod
    def new_client():
        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
