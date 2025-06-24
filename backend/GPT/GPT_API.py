# GPT/gpt_api.py
from openai import OpenAI

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")

    api_key="sk-uq5HEFeqkelo8PO040D49d8042Aa4f819f46De28441408Cb",
    #base_url="https://api.chatanywhere.tech/v1"
    base_url="https://free.v36.cm/v1"
)
# 非流式响应
def gpt_api(messages: list):
    completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def gpt_api_stream(messages: list):
    stream = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
