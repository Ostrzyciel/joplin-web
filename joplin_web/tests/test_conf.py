# coding: utf-8
from django.conf import settings
from django.test import TestCase


class JoplinWebSettingsTestCase(TestCase):

    """
      check that all the needed config is present
    """

    def test_get_config_service(self):
        self.assertIs(type(settings.JOPLIN_WEBCLIPPER_TOKEN), str)
