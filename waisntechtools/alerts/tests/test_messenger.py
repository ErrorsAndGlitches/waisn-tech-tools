import tempfile

from django.test import TestCase

from alerts.messenger import Messenger, Message
from alerts.models import Subscriber


class MessageTestCase(TestCase):
    def test_message(self):
        temp = tempfile.NamedTemporaryFile()
        temp.write('The test has completed'.encode(encoding='utf-8'))
        temp.flush()
        read_message = Message(temp.name).contents()
        self.assertEqual(read_message, 'The test has completed')
