from transitions import Machine
from twilio.rest import Client

from django.conf import settings
from .asset_files import AssetFiles


class SubscriptionStates(object):
    UNSUBSCRIBED_STATE = "unsubscribed"
    SELECTING_LANG_STATE = "selecting_language"
    COMPLETE_STATE = "complete"
    INITIAL_STATE = UNSUBSCRIBED_STATE

    _SRC = "source"
    _DST = "dest"
    _TRIGGER = "trigger"
    _AFTER = "after"
    _BEFORE = "before"

    _STATES = [
        UNSUBSCRIBED_STATE,
        SELECTING_LANG_STATE,
        COMPLETE_STATE
    ]

    _TRANSITIONS = [
        {
            _TRIGGER: "subscribe_help",
            _SRC: UNSUBSCRIBED_STATE,
            _DST: UNSUBSCRIBED_STATE,
            _AFTER: "_subscribe_help"
        },
        {
            _TRIGGER: "start_subscription",
            _SRC: UNSUBSCRIBED_STATE,
            _DST: SELECTING_LANG_STATE,
            _AFTER: "_start_subscription"
        },
        {
            _TRIGGER: "unknown_lang_selected",
            _SRC: SELECTING_LANG_STATE,
            _DST: SELECTING_LANG_STATE,
            _AFTER: "_unknown_lang_selected"
        },
        {
            _TRIGGER: "lang_selected",
            _SRC: SELECTING_LANG_STATE,
            _DST: COMPLETE_STATE,
            _AFTER: "_lang_selected"
        },
        {
            _TRIGGER: "complete_state_help",
            _SRC: COMPLETE_STATE,
            _DST: COMPLETE_STATE,
            _AFTER: "_complete_state_help"
        },
        {
            _TRIGGER: "reselect_language",
            _SRC: COMPLETE_STATE,
            _DST: SELECTING_LANG_STATE,
            _AFTER: "_reselect_language"
        },
        {
            _TRIGGER: "end_subscription",
            _SRC: COMPLETE_STATE,
            _DST: UNSUBSCRIBED_STATE,
            _AFTER: "_end_subscription"
        },
    ]

    def __init__(self, subscriber, messenger):
        if subscriber.subscription_state not in SubscriptionStates._STATES:
            raise Exception("Unknown state: {}".format(
                subscriber.subscription_state))

        self._subscriber = subscriber
        self._machine = Machine(
            model=self,
            states=SubscriptionStates._STATES,
            initial=subscriber.subscription_state,
            transitions=SubscriptionStates._TRANSITIONS
        )
        self._messenger = messenger

    def _subscribe_help(self):
        self._send_msgs(
            [AssetFiles(self._subscriber.language).subscribe_help_file()])

    def _start_subscription(self):
        self._subscriber.subscription_state = SubscriptionStates.SELECTING_LANG_STATE
        self._subscriber.save()
        self._send_msgs([
            AssetFiles(self._subscriber.language).welcome_file(),
            AssetFiles(self._subscriber.language).lang_select_file()
        ])

    def _unknown_lang_selected(self):
        self._send_msgs([
            AssetFiles(self._subscriber.language).unsupported_lang_file(),
            AssetFiles(self._subscriber.language).lang_select_file()
        ])

    def _lang_selected(self, iso_code):
        self._subscriber.subscription_state = SubscriptionStates.COMPLETE_STATE
        self._subscriber.language = iso_code
        self._subscriber.save()
        self._send_msgs(
            [AssetFiles(self._subscriber.language).confirmation_file()])

    def _complete_state_help(self):
        self._send_msgs([AssetFiles(self._subscriber.language).error_file()])

    def _reselect_language(self):
        self._subscriber.subscription_state = SubscriptionStates.SELECTING_LANG_STATE
        self._subscriber.save()
        self._send_msgs(
            [AssetFiles(self._subscriber.language).lang_select_file()])

    def _end_subscription(self):
        self._send_msgs(
            [AssetFiles(self._subscriber.language).unsubscribe_file()])
        self._subscriber.delete()

    def _send_msgs(self, filenames):
        self._messenger.send(self._subscriber, filenames)
