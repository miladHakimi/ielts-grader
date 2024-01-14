import os

from openai import OpenAI


# ChatGPT Interface
class ChatGPT:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
        )

    # Puts the requests to the "to be processed" queue.
    def enqueue(self, req):
        pass

    # Reads a request from the queue and returns it.
    def dequeue(self):
        pass

    # Sends the request to the ChatGPT server and returns the response.
    def prompt(self, req):
        response = self.client.chat.completions.create(model="gpt-3.5-turbo",
                                messages=[{
                                    "role": "user",
                                    "content": req
                                    }])
        return response.choices[0].message.content
