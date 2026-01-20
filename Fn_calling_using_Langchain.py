import os
import json
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from dotenv import load_dotenv
load_dotenv()

@tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """
    Get current weather information for a specific location

    Args:
        location (str): The city and state, e.g. San Francisco, CA
        unit (str): The temperature unit to use (celsius or fahrenheit)

    """
    return json.dumps({
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 60
    })

deployment_model = "gpt-4o"
llm = AzureChatOpenAI(
    api_key          = os.environ["AZURE_OPENAI_API_KEY"],
    api_version      = "2025-04-01-preview",
    azure_endpoint   = "https://ai-proxy.lab.epam.com",
    azure_deployment = deployment_model
).bind_tools([get_weather])

msgs = [HumanMessage(content="What's the weather like in New York, NY?")]
res = llm.invoke(msgs)
print("AI Response:", res.content)

for call in getattr(res, "tool_calls", []):
    out = get_weather.invoke(call["args"])
    msgs += [res, ToolMessage(content=out, tool_call_id=call["id"])]
    res = llm.invoke(msgs)
    print("\nFinal AI Response:", res.content)