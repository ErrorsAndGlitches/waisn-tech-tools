from django.test import LiveServerTestCase, override_settings
from django.urls import reverse

from alerts.models import Subscriber
from alerts.languages import Language
from alerts.subscription_states import SubscriptionStates


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class SubscriptionProcessTests(LiveServerTestCase):
    _PHONE_NUMBER = '+1234567890'

    def test_subscribe_unsubscribe(self):
        self._verify_interaction('join', SubscriptionStates.SELECTING_LANG_STATE)
        self._verify_interaction('1', SubscriptionStates.COMPLETE_STATE)
        self._send_twilio_message('leave')
        self.assertEqual(0, len(Subscriber.objects.all()))

    def test_change_language(self):
        self._verify_interaction('join', SubscriptionStates.SELECTING_LANG_STATE)
        self._verify_interaction('1', SubscriptionStates.COMPLETE_STATE)
        self._verify_interaction('change language', SubscriptionStates.SELECTING_LANG_STATE)
        self._verify_interaction('2', SubscriptionStates.COMPLETE_STATE, Language.SPANISH)
        self._send_twilio_message('leave')
        self.assertEqual(0, len(Subscriber.objects.all()))

    def test_resubscribe(self):
        for _ in range(0, 3):
            self._verify_interaction('join', SubscriptionStates.SELECTING_LANG_STATE)
            self._verify_interaction('1', SubscriptionStates.COMPLETE_STATE)
            self._send_twilio_message('leave')
            self.assertEqual(0, len(Subscriber.objects.all()))

    def _verify_interaction(self, body, expected_state, expected_lang=Language.ENGLISH):
        self._send_twilio_message(body)

        subscribers = Subscriber.objects.all()
        self.assertEqual(1, len(subscribers))

        subscriber = subscribers[0]
        self.assertEqual(self._PHONE_NUMBER, subscriber.phone_number)
        self.assertEqual(expected_lang, subscriber.language)
        self.assertEqual(expected_state, subscriber.subscription_state)

    def _send_twilio_message(self, body):
        response = self.client.post(
            reverse('alerts:subscribe'),
            {'From': self._PHONE_NUMBER, 'Body': body}
        )
        self.assertEqual(response.status_code, 200)
