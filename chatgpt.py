import os

import openai


# ChatGPT Interface
class ChatGPT:

    def __init__(self):
        openai.api_key = os.environ.get('OPENAI_API_KEY')

    # Puts the requests to the "to be processed" queue.
    def enqueue(self, req):
        pass

    # Reads a request from the queue and returns it.
    def dequeue(self):
        pass

    # Sends the request to the ChatGPT server and returns the response.
    def prompt(self, req):
        response = openai.Completion.create(model="text-davinci-003",
                                            prompt=req,
                                            temperature=0.9,
                                            max_tokens=1000)
        return response
