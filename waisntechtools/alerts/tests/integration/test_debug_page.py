from django.test import LiveServerTestCase, override_settings
from django.utils import timezone
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from alerts.languages import Language
from alerts.models import Subscriber
from alerts.subscription_states import SubscriptionStates


@override_settings(WAISN_AUTH_ENABLED=False, DEBUG=True, TEST=True)
class DebugPageTests(LiveServerTestCase):
    _PHONE_NUMBER = '+1234567890'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")
        cls.selenium = WebDriver(firefox_options=opts)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_debug_page(self):
        subscriber, _ = Subscriber.objects.get_or_create(
            phone_number=self._PHONE_NUMBER,
            defaults={
                'language': Language.DEFAULT_LANGUAGE,
                'subscription_state': SubscriptionStates.INITIAL_STATE,
                'date_registered': timezone.now(),
            })

        subscriber, _ = Subscriber.objects.get_or_create(
            phone_number=reversed(self._PHONE_NUMBER),
            defaults={
                'language': Language.DEFAULT_LANGUAGE,
                'subscription_state': SubscriptionStates.INITIAL_STATE,
                'date_registered': timezone.now(),
            })
        self.selenium.get('{}/alerts/debug'.format(self.live_server_url))

        subscriber_list = self.selenium.find_element_by_id('subscribers-list')
        self.assertEqual(2, len(subscriber_list.find_elements_by_tag_name('li')))
