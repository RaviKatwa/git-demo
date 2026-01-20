
import os
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key        = os.environ["AZURE_OPENAI_API_KEY"],
    api_version    = "2025-04-01-preview",
    azure_endpoint = "https://ai-proxy.lab.epam.com",
)

deployment_model = "gpt-4o"

messages: list[ChatCompletionMessageParam] = [
   {"role": "system", "content": "You are a helpful assistant."}
]

while True:
    user_input = input("User: ")
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model    = deployment_model,
        messages = messages,
    )

    assistant_message = response.choices[0].message
    messages.append({
        "role": "assistant", "content": assistant_message.content
    })

    print("Assistant: ", assistant_message.content)