from django.conf import settings
from twilio.rest import Client
from unittest.mock import MagicMock

import sys


def get_twilio_cred():
    if 'test' in sys.argv:
        mock = MagicMock()
        mock.__iter__.return_value = []
        return mock

    else:
        client = Client(settings.TWILIO_ACCOUNT_SID,
                        settings.TWILIO_AUTH_TOKEN)
        return client
