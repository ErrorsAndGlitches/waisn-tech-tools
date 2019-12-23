from django.shortcuts import render
from django.views.generic import TemplateView

from alerts.models import Subscriber
from alerts.waisn_auth import waisn_auth

from .get_twilio_cred import get_twilio_cred


def get_post_request(get_handler, post_handler):
    def _handle_request(request):
        if request.method == 'POST':
            return post_handler(request)
        else:
            return get_handler(request)

    return _handle_request


@waisn_auth
def index(request):
    return render(request, 'alerts/index.html')


@waisn_auth
def debug(request):
    return DebugView.as_view()(request)


class DebugView(TemplateView):
    template_name = 'alerts/debug.html'

    def recent_twilio_messages(self):
        client = get_twilio_cred()
        messages_list = client.messages.list(limit=10)
        return messages_list

    def get_context_data(self, **kwargs):
        context = super(DebugView, self).get_context_data(**kwargs)
        context['messages'] = self.recent_twilio_messages()
        context['subscribers'] = Subscriber.objects.order_by(
            '-date_registered')
        return context
