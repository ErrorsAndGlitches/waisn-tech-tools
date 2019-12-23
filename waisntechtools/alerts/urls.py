from django.urls import path
from alerts import views, alert_request, follow_up_request, twilio_app
import requests

app_name = 'alerts'
urlpatterns = [
    path('', views.index, name='index'),
    path('debug', views.debug, name='debug'),
    path('alert', alert_request.index, name='alert'),
    path('alert/sent', alert_request.sent, name='alert_sent'),
    path('follow-up', follow_up_request.index, name='follow_up'),
    path('follow-up/sent', follow_up_request.sent, name='follow_up_sent'),
    path('subscribe',
         twilio_app.handle, name='subscribe'),
]
