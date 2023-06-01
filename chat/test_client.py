import time
import unittest
from client import ChatClient
from resp import *
import subprocess


class TestChatClient(unittest.TestCase):
    def setUp(self) -> None:
        self.host = "127.0.0.1"
        self.port = 8888
        self.p = subprocess.Popen(['python', 'chat_server.py', f'--port={self.port}'])

    def doCleanups(self):
        self.p.kill()
        time.sleep(1)

    def test_send_presence_wrong_port(self):
        with self.assertRaises(ConnectionRefusedError) as context:
            ChatClient(self.host, self.port+1).send_presence()
        self.assertTrue('Error' in str(context.exception))

    def test_send_presence(self):
        self.assertEqual(ChatClient(self.host, self.port).send_presence(), OK_200)

    def test_send_msg(self):
        self.assertEqual(ChatClient(self.host, self.port).send_msg('{ "message": "some text" }'), OK_200)

    def test_send_msg_wrong_json(self):
        self.assertEqual(ChatClient(self.host, self.port).send_msg("some wrong data"), WRONG_JSON_OR_REQUEST_400)


if __name__ == "__main__":
    unittest.main()
