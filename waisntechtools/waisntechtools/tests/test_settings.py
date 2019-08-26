from django.test import TestCase
from importlib import reload
from os import environ
import waisntechtools.settings.common


class CommonSettingsTests(TestCase):
    def test_default_auth_setting(self):
        reload(waisntechtools.settings.common)
        from waisntechtools.settings.common import WAISN_AUTH_ENABLED
        self.assertTrue(WAISN_AUTH_ENABLED)

    def test_auth_false_override(self):
        self._test_environ_var_set("FALSE", False)

    def test_auth_true_override(self):
        self._test_environ_var_set("TRUE", True)

    def test_auth_garbage_override(self):
        self._test_environ_var_set("garbage", False)

    def _test_environ_var_set(self, value, expectedBoolean):
        environ['WAISN_AUTH_ENABLED'] = value
        reload(waisntechtools.settings.common)
        from waisntechtools.settings.common import WAISN_AUTH_ENABLED
        self.assertEqual(WAISN_AUTH_ENABLED, expectedBoolean)
