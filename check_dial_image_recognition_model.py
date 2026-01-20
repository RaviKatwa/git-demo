import os
import requests
from dotenv import load_dotenv
load_dotenv()


def get_model_limits(model: dict):
    """Check if the model has usage limits set (indicating availability)."""
    try:
        limits = requests.get(
            f"https://ai-proxy.lab.epam.com/v1/deployments/{model['id']}/limits",
            headers={"Api-Key": os.environ["AZURE_OPENAI_API_KEY"]},
            timeout=20
        ).json()
        minute_limit = limits.get("minuteTokenStats", {}).get("total", 0)
        day_limit = limits.get("dayTokenStats", {}).get("total", 0)
        if minute_limit > 0 or day_limit > 0:
            return {model['id']: {"limits": {"minute": minute_limit, "day": day_limit}}}
    except:
        pass


models = requests.get(
    "https://ai-proxy.lab.epam.com/openai/models",
    headers={"Api-Key": os.environ["AZURE_OPENAI_API_KEY"]},
    timeout=20
).json()["data"]

print("DIAL supports these models:")
for model in models:
    if 'Image Recognition' in model['description_keywords']:
        is_available_to_you = get_model_limits(model)
        print("  ->", model['id'], "(available)" if is_available_to_you else "(not available)")