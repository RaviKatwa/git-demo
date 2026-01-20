import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
deployment_model = "dall-e-3"
api_version = "2025-04-01-preview"
headers = {
    "Api-Key": os.environ["AZURE_OPENAI_API_KEY"],
}

# Fetch deployment configuration (optional, for debugging)
response = requests.get(
    f"https://ai-proxy.lab.epam.com/v1/deployments/{deployment_model}/configuration",
    headers=headers
).json()
print("Deployment Configuration:", json.dumps(response, indent=3))

# Payload for image generation
payload = {
    "messages": [
        {
            "role": "user",
            "content": "Generate an image of a cat with a hat on a beach"
        }
    ],
    "custom_fields": {
        "configuration": {
            "size": "1792x1024"
        }
    }
}

# Send request to generate the image
# Send request to generate the image
image_response = requests.post(
    f"https://ai-proxy.lab.epam.com/openai/deployments/{deployment_model}/chat/completions?api-version={api_version}",
    headers=headers,
    json=payload
)

# Check if the request was successful
if image_response.status_code == 200:
    result = image_response.json()
    print("Full Response:", json.dumps(result, indent=3))  # Debugging step

    # Update this part based on the actual response structure
    image_url = result.get("image_url")  # Replace "image_url" with the correct key
    if image_url:
        # Download the image
        image_data = requests.get(image_url).content
        with open("cat_with_hat_on_beach.png", "wb") as image_file:
            image_file.write(image_data)
        print("Image saved as 'cat_with_hat_on_beach.png'")
    else:
        print("Image URL not found in the response. Please check the response structure.")
else:
    print(f"Failed to generate image. Status code: {image_response.status_code}")
    print("Error:", image_response.text)