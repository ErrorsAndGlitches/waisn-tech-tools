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
        lambda r: render(r, 'alerts/follow_up_request.html', {'form': FollowUpRequestForm()}),
        _follow_up_form_submission
    )(request)


@waisn_auth
def sent(request):
    return FollowUpSentView.as_view()(request)


def _follow_up_form_submission(request):
    form = FollowUpRequestForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest('Invalid form input')
    data = form.cleaned_data
    MassNotification.create().send(Notification(
        AssetFiles.follow_up_file,
        {
            'num_people': data['num_people'], 'city': data['city'], 'target_name': data['target_name'],
            'target_phone_num': data['target_phone_num']
        }
    ))
    return HttpResponseRedirect(reverse('alerts:follow_up_sent'))


class FollowUpRequestForm(forms.Form):
    _PHONE_NUMBER_FORMAT = '###-###-####'

    num_people = forms.IntegerField(label='Number People Detained', min_value=0)
    city = forms.CharField(label='City', max_length=200)
    target_name = forms.CharField(label='Person to Call for Release', max_length=200)
    target_phone_num = forms.CharField(
        label='Phone Number of Person to Call (format is {})'.format(_PHONE_NUMBER_FORMAT),
        max_length=len(_PHONE_NUMBER_FORMAT)
    )


class FollowUpSentView(ListView):
    model = Subscriber
    template_name = 'alerts/follow_up_sent.html'
    context_object_name = 'subscribers'

    def get_queryset(self):
        return Subscriber.objects \
            .filter(subscription_state=SubscriptionStates.COMPLETE_STATE) \
            .order_by('-date_registered')
