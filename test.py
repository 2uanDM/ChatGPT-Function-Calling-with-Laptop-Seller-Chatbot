import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI"),
)

stream = client.chat.completions.create(
    model='gpt-3.5-turbo-1106',
    stream=True,
    response_format={
        'type': 'json_object'
    },
    messages=[
        {
            'role': 'user',
            'content': 'Can you code for me the quicksort algorithm?. The output must be in json object like this {"status": "success", "code": ...}'
        }
    ]
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:  # check if the model has responded
        print(chunk.choices[0].delta.content, end="")  # print the response
