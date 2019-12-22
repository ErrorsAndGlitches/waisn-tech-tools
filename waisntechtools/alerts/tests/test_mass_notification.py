from django.test import TestCase
from unittest.mock import Mock

from alerts.asset_files import AssetFiles
from alerts.languages import Language
from alerts.mass_notification import Notification, MassNotification


class MassNotificationTests(TestCase):
    def test_notification_substitution(self):
        body = Notification(AssetFiles.action_alert_file, {'address': '111 2nd Street'}).body(Language.ENGLISH)
        self.assertEqual(
            body,
            'ICE activity has been confirmed at 111 2nd Street. Please take caution or show up if you are able to support.'
        )

    def test_mass_notification(self):
        sns = Mock()
        mass_notification = MassNotification(sns, [self._mock_subscriber(i) for i in range(0, 10)])
        mass_notification.send(self._mock_notification())
        self.assertEqual(10, sns.publish.call_count)

    @staticmethod
    def _mock_subscriber(phone_number):
        subs = Mock()
        subs.phone_number = phone_number
        subs.language = Language.ENGLISH
        return subs

    @staticmethod
    def _mock_notification():
        notification = Mock()
        notification.body.return_value = 'body'
        return notification
