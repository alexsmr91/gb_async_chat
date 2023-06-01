import unittest
from server import ChatServer
from resp import *


class TestChatServer(unittest.TestCase):
    def setUp(self) -> None:
        self.host = "127.0.0.1"
        self.port = 8888

    def test_wrong_addr(self):
        with self.assertRaises(Exception) as context:
            ChatServer("300.0.0.1", self.port)
        self.assertTrue('Errno' in str(context.exception))

    def test_wrong_port(self):
        with self.assertRaises(Exception) as context:
            ChatServer(self.host, 80000)
        self.assertTrue('getsockaddrarg' in str(context.exception))

    def test_decode_wrong_data(self):
        self.assertEqual(ChatServer(self.host, self.port).load_json_or_none("some wrong data"), None)

    def test_decode(self):
        self.assertEqual(ChatServer(self.host, self.port).load_json_or_none("{}"), {})

    def test_decode2(self):
        self.assertEqual(ChatServer(self.host, self.port).load_json_or_none('{"key": "value"}'), {"key": "value"})


if __name__ == "__main__":
    unittest.main()
