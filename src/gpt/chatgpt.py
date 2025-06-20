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
        response = self.client.chat.completions.create(model="gpt-4o-2024-08-06",
                                messages=[{
                                    "role": "user",
                                    "content": req
                                    }],
                                    temperature=0.6,)
        return response.choices[0].message.content
