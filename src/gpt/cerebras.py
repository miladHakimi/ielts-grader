import os

from .chatgpt import ChatGPT
from cerebras.cloud.sdk import Cerebras


# CerebrasGPT Interface
class CerebrasGPT(ChatGPT):

    def __init__(self):
        self.client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

    # Puts the requests to the "to be processed" queue.
    def enqueue(self, req):
        pass

    # Reads a request from the queue and returns it.
    def dequeue(self):
        pass

    # Sends the request to the ChatGPT server and returns the response.
    def prompt(self, req):
        completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": req,
                }
            ],
            model="llama3.1-70b",
            temperature=1
        )
        print("req:", req)
        return completion.choices[0].message.content
