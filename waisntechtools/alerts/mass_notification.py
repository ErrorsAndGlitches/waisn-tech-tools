import logging
from string import Template
from unittest.mock import Mock

import boto3
from django.conf import settings

from alerts.asset_files import AssetFiles
from alerts.messenger import Message
from alerts.models import Subscriber
from alerts.subscription_states import SubscriptionStates

logger = logging.getLogger(__name__)


class MassNotification(object):
    @staticmethod
    def create():
        return MassNotification(
            MassNotification._sns_client(),
            Subscriber.objects.filter(subscription_state=SubscriptionStates.COMPLETE_STATE)
        )

    @staticmethod
    def _sns_client():
        if settings.TEST:
            logger.warning("Test is enabled. Using mock SNS client")
            return Mock()
        else:
            return boto3.client('sns', region_name="us-west-2")

    def __init__(self, sns_client, subscribers):
        self._sns_client = sns_client
        self._subscribers = subscribers

    def send(self, notification):
        for subscriber in self._subscribers:
            self._sns_client.publish(
                PhoneNumber=subscriber.phone_number,
                Message=notification.body(subscriber.language)
            )
        logger.info("Sent {} notifications for {}", len(self._subscribers), notification)


class Notification(object):
    def __init__(self, file_func, substitutions):
        self._file_func = file_func
        self._substitutions = substitutions
        self._cached_contents = {}

    def body(self, language):
        if language in self._cached_contents:
            return self._cached_contents[language]

        file = self._file_func(AssetFiles(language))
        msg = Template(Message(file).contents()).substitute(self._substitutions)
        self._cached_contents[language] = msg
        return msg

    def __str__(self):
        return self._file_func
