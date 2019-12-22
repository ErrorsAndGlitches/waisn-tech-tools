from django import forms
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from alerts.models import Subscriber
from alerts.subscription_states import SubscriptionStates
from alerts.views import get_post_request
from alerts.waisn_auth import waisn_auth
from alerts.mass_notification import MassNotification, Notification
from alerts.asset_files import AssetFiles


@waisn_auth
def index(request):
    return get_post_request(
        lambda r: render(r, 'alerts/alert_request.html', {'form': AlertRequestForm()}),
        _alert_form_submission
    )(request)


@waisn_auth
def sent(request):
    return AlertSentView.as_view()(request)


def _alert_form_submission(request):
    form = AlertRequestForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest('Invalid form input')
    data = form.cleaned_data
    MassNotification.create().send(Notification(AssetFiles.action_alert_file, {'address': data['address']}))
    return HttpResponseRedirect(reverse('alerts:alert_sent'))


class AlertRequestForm(forms.Form):
    address = forms.CharField(label='Event Address', max_length=100)


class AlertSentView(ListView):
    model = Subscriber
    template_name = 'alerts/alert_sent.html'
    context_object_name = 'subscribers'

    def get_queryset(self):
        return Subscriber.objects \
            .filter(subscription_state=SubscriptionStates.COMPLETE_STATE) \
            .order_by('-date_registered')
