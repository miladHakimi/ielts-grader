# This file contains tests for ChatGPT Interface.
import unittest
import chatgpt

class CreationTests(unittest.TestCase):
    """Test creation."""

    def test_creation(self):
        api = chatgpt.ChatGPT()
        self.assertIsNotNone(api)
        try:
            response = api.prompt("Hey GPT, do you copy?")
            self.assertIsNotNone(response.choices and response.choices[0].text)
        except Exception as e:
            self.fail("Exception raised: {}".format(e))

if __name__ == '__main__':
    unittest.main()