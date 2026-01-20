import os
import json
from agents import Agent, Runner, set_tracing_disabled, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv
load_dotenv()

set_tracing_disabled(disabled=True)

@function_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """
    Get current weather information for a specific location

    Args:
        location (str): The city and state, e.g., San Francisco, CA
        unit (str): The temperature unit to use (celsius or fahrenheit)

    """
    weather_data = {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 60
    }
    return json.dumps(weather_data)

os.environ["AZURE_API_KEY"]     = os.environ["AZURE_OPENAI_API_KEY"]
os.environ["AZURE_API_BASE"]    = "https://ai-proxy.lab.epam.com"
os.environ["AZURE_API_VERSION"] = "2025-04-01-preview"

deployment_model = "azure/gpt-4o"
agent = Agent(
    model        = LitellmModel(deployment_model),
    name         = "Assistant",
    instructions = "You are a helpful assistant with access to weather information.",
    tools        = [get_weather]
)
result = Runner.run_sync(agent, "What is the weather like in Tokyo, Japan?")
print(result.final_output)