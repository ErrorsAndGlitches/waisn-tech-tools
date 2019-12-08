from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from alerts import alert_request, follow_up_request, subscription_app, views
from alerts.subscription_app import SubscriptionApp

app_name = 'alerts'
sub_app = SubscriptionApp()
urlpatterns = [
    path('', views.index, name='index'),
    path('debug', views.debug, name='debug'),
    path('alert', alert_request.index, name='alert'),
    path('alert/sent', alert_request.sent, name='alert_sent'),
    path('follow-up', follow_up_request.index, name='follow_up'),
    path('follow-up/sent', follow_up_request.sent, name='follow_up_sent'),
    path('subscribe', csrf_exempt(sub_app.handle), name='subscribe'),
]
