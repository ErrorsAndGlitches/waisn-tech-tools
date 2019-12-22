from django.conf import settings
from unittest.mock import Mock
from twilio.rest import Client

import logging
logger = logging.getLogger(__name__)


class TwilioClientFactory(object):

    @staticmethod
    def new_client():
        if settings.TEST:
            logger.warning("Test is enabled. Using mock Twilio client")
            twilio_mock = Mock()
            twilio_mock.messages.list.return_value = []
            return twilio_mock
        else:
            return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
