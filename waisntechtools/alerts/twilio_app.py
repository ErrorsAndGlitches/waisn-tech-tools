from django.utils import timezone
from django.http import HttpResponse
from django_twilio.decorators import twilio_view

from .messenger import Messenger
from .models import Subscriber
from .languages import Language, MessagePhraseConditions, UnknownLanguageId
from .subscription_states import SubscriptionStates


@twilio_view
def handle(request):
    phone_number = request.POST.get('From')
    message_body = request.POST.get('Body').lower()
    subscriber, _ = Subscriber.objects.get_or_create(
        phone_number=phone_number,
        defaults={
            'language': Language.DEFAULT_LANGUAGE,
            'subscription_state': SubscriptionStates.INITIAL_STATE,
            'date_registered': timezone.now(),
        })

    messenger = Messenger()
    subscriber_state = SubscriptionStates(subscriber, messenger)
    courier = SubscriptionCourier(subscriber, subscriber_state, message_body)

    try:
        courier.receive()
        return HttpResponse(status=200)
    except Exception as e:
        print("There is an error: {}".format(e))
        return HttpResponse(status=500)


class SubscriptionCourier(object):
    def __init__(self, subscriber, subscriber_state, message_body):
        self._subscriber = subscriber
        self._subscriber_state = subscriber_state
        self._message_body = message_body
        self._handled_msgs = {
            SubscriptionStates.UNSUBSCRIBED_STATE: self._on_unsubscribed_state,
            SubscriptionStates.SELECTING_LANG_STATE: self._on_select_lang_state,
            SubscriptionStates.COMPLETE_STATE: self._on_complete_state
        }

    def receive(self):
        self._handled_msgs[self._subscriber.subscription_state](
            self._message_body)

    def _on_unsubscribed_state(self, *args):
        if MessagePhraseConditions(self._message_body).is_join_msg():
            self._subscriber_state.start_subscription()
        else:
            self._subscriber_state.subscribe_help()

    def _on_select_lang_state(self, *args):
        try:
            iso_code = Language.language_code(self._message_body)
            self._subscriber_state.lang_selected(iso_code)
        except UnknownLanguageId:
            self._subscriber_state.unknown_lang_selected()

    def _on_complete_state(self, *args):
        if MessagePhraseConditions(self._message_body).is_change_lang_msg():
            self._subscriber_state.reselect_language()
        elif MessagePhraseConditions(self._message_body).is_leave_msg():
            self._subscriber_state.end_subscription()
        else:
            self._subscriber_state.complete_state_help()
