from unittest.mock import Mock

from django.test import TestCase

from alerts.languages import *
from alerts.models import Subscriber
from alerts.subscription_states import SubscriptionStates


class SubscriptionStateTestCase(TestCase):
    def setUp(self) -> None:
        self._msgr = Mock()

    def test_subscription_state_constructor(self):
        SubscriptionStates(self.subscriber(SubscriptionStates.INITIAL_STATE), self._msgr)

    def test_subscribe_help(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.UNSUBSCRIBED_STATE), self._msgr)
        state.subscribe_help()
        self.assert_messenger_state(filenames=["alerts/assets/eng/subscribe_help_msg.txt"])

    def test_start_subscription(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.UNSUBSCRIBED_STATE), self._msgr)
        state.start_subscription()
        self.assert_messenger_state(filenames=[
            "alerts/assets/eng/welcome_msg.txt",
            "alerts/assets/eng/language_selection_msg.txt"
        ])

    def test_unknown_lang_selected(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.SELECTING_LANG_STATE), self._msgr)
        state.unknown_lang_selected()
        self.assert_messenger_state(filenames=[
            "alerts/assets/eng/unsupported_lang_msg.txt",
            "alerts/assets/eng/language_selection_msg.txt"
        ])

    def test_lang_selected(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.SELECTING_LANG_STATE), self._msgr)
        state.lang_selected("spa")
        self.assert_messenger_state(filenames=["alerts/assets/spa/confirmation_msg.txt"])

    def test_complete_state_help(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.COMPLETE_STATE), self._msgr)
        state.complete_state_help()
        self.assert_messenger_state(filenames=["alerts/assets/eng/error_msg.txt"])

    def test_reselect_language(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.COMPLETE_STATE), self._msgr)
        state.reselect_language()
        self.assert_messenger_state(filenames=["alerts/assets/eng/language_selection_msg.txt"])

    def test_end_subscription(self):
        state = SubscriptionStates(self.subscriber(SubscriptionStates.COMPLETE_STATE), self._msgr)
        state.end_subscription()
        self.assert_messenger_state(filenames=["alerts/assets/eng/unsubscribed_msg.txt"])

    @staticmethod
    def subscriber(state) -> Subscriber:
        sub = Mock()
        sub.subscription_state = state
        sub.language = Language.ENGLISH
        sub.phone_number = "+11234567890"
        return sub

    def assert_messenger_state(self, filenames) -> None:
        assert self._msgr.send.call_count == 1

        for index, filename in enumerate(filenames):
            self.assertEqual(
                self._msgr.send.call_args[0][1][index],
                filename
            )
