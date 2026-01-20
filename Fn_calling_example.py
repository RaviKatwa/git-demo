
import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

def get_weather(location: str, unit: str = "celsius") -> str:
    """Mock function to get weather information""" 
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 60
    }
    return json.dumps(weather_data)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant with access to weather information."
    },
    {
        "role": "user",
        "content": "What is the weather like in Tokyo, Japan?"
    }
]

client = AzureOpenAI(
    api_key        = os.environ["AZURE_OPENAI_API_KEY"],
    api_version    = "2025-04-01-preview", 
    azure_endpoint = "https://ai-proxy.lab.epam.com"
)

deployment_model = "gpt-4o"
response = client.chat.completions.create(
    model       = deployment_model,
    messages    = messages,
    tools       = tools,
    tool_choice = "auto"
)

print(response.choices[0].finish_reason)
print(response.choices[0].message.content)
print(response.choices[0].message.tool_calls)

tool = response.choices[0].message.tool_calls[0]
print(tool.id)
print(tool.function.name)
print(tool.function.arguments)

response_message = response.choices[0].message
if response_message.tool_calls:
    messages.append({
        "role": "assistant",
        "content": response_message.content,
        "tool_calls": response_message.tool_calls
    })

    for tool_call in response_message.tool_calls:
        if tool_call.function.name == "get_weather":
            function_args = json.loads(tool_call.function.arguments)
            function_response = get_weather(
                location=function_args.get("location"),
                unit=function_args.get("unit", "celsius")
            )
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": function_response
            })

final_response = client.chat.completions.create(
    model=deployment_model,
    messages=messages,
    tools=tools,
)

print("Final messages array:")
for msg in messages:
    print(msg)

print(final_response.choices[0].message.content)