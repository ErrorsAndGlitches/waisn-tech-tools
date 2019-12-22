from bs4 import BeautifulSoup
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.core.management.commands import flush
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock

from alerts.tests.fakes import SubscriberFactory


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class IndexViewTests(TestCase):
    _STATIC_PREFIX = '/static/'

    def test_home_page_static_content(self):
        response = self.client.get(reverse('alerts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'WAISN')

        static_imgs = [
            img['src'][len(IndexViewTests._STATIC_PREFIX):]
            for img in BeautifulSoup(response.content, 'html.parser').find_all("img")
            if IndexViewTests._is_static_resource(img['src'])
        ]

        for static_img in static_imgs:
            self.assertIsNotNone(finders.find(static_img))

    @staticmethod
    def _is_static_resource(resource):
        return resource.startswith(IndexViewTests._STATIC_PREFIX)


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class DebugViewTests(TestCase):
    def setUp(self):
        call_command(flush.Command(), interactive=False)

    def tearDown(self):
        call_command(flush.Command(), interactive=False)

    @patch("alerts.twilio.TwilioClientFactory.new_client")
    def test_list_length(self, mock_new_client):
        mock_client = Mock()
        mock_client.messages.list.return_value = []
        mock_new_client.return_value = mock_client

        num_subscribers = 10
        for _ in range(0, num_subscribers):
            SubscriberFactory.create()

        response = self.client.get(reverse('alerts:debug'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subscribers']), 10)


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class AlertViewTests(TestCase):
    def test_alert_notification_page(self):
        response = self.client.get(reverse('alerts:alert'))
        self.assertContains(response, 'Alert Notification')
        self.assertIsNotNone(response.context['form'])

    def test_alert_submission(self):
        response = self.client.post(reverse('alerts:alert'), data={
            'address': '0123 Awesome Str'
        })
        self.assertRedirects(response, reverse('alerts:alert_sent'))

    def test_alert_sent_page(self):
        response = self.client.get(reverse('alerts:alert_sent'))
        self.assertContains(response, 'Alert Notification Successfully Sent')


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class FollowUpViewTests(TestCase):
    def test_follow_up_page(self):
        response = self.client.get(reverse('alerts:follow_up'))
        self.assertContains(response, 'Follow Up Notification')
        self.assertIsNotNone(response.context['form'])

    def test_alert_submission(self):
        response = self.client.post(reverse('alerts:follow_up'), data={
            'num_people': '123',
            'city': 'Seattle',
            'target_name': 'Will The Wise',
            'target_phone_num': '123-456-7890'
        })
        self.assertRedirects(response, reverse('alerts:follow_up_sent'))

    def test_alert_sent_page(self):
        response = self.client.get(reverse('alerts:follow_up_sent'))
        self.assertContains(response, 'Follow Up Notification Successfully Sent')
