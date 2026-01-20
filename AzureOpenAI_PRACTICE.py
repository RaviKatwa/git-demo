import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

# Creating the AzureOpenAI client with EPAM DIAL endpoint
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2025-04-01-preview",
    azure_endpoint="https://ai-proxy.lab.epam.com"
)

# Preparing messages for the chat completion
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "What is the capital of Japan?"
    }
]

# Setting the deployment model
deployment_model = "gpt-4o"

# Creating chat completion request
response = client.chat.completions.create(
    model=deployment_model,
    messages=messages,
)

# Printing the response content
print(response.choices[0].message.content)