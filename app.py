import subprocess
import sys
import os
from databricks.sdk import WorkspaceClient

# Ensure environment variables are set
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
SERVING_ENDPOINT = os.getenv("SERVING_ENDPOINT")

if not DATABRICKS_HOST or not DATABRICKS_TOKEN or not SERVING_ENDPOINT:
    raise ValueError("Please ensure DATABRICKS_HOST, DATABRICKS_TOKEN, and SERVING_ENDPOINT are set.")

# Initialize Databricks WorkspaceClient
client = WorkspaceClient(
    host=DATABRICKS_HOST,
    token=DATABRICKS_TOKEN
)
# Upgrade typing_extensions FIRST (before any imports that need it)
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "typing_extensions", "-q"])

# Install full mlflow (not mlflow-skinny) before importing model_serving_utils
subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "mlflow-skinny"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.check_call([sys.executable, "-m", "pip", "install", "mlflow", "-q"])

# Install required dependencies
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "-q"])
    import streamlit as st

import logging
from model_serving_utils import query_endpoint, is_endpoint_supported

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure environment variable is set correctly
SERVING_ENDPOINT = os.getenv('SERVING_ENDPOINT')
assert SERVING_ENDPOINT, \
    ("Unable to determine serving endpoint to use for chatbot app. If developing locally, "
     "set the SERVING_ENDPOINT environment variable to the name of your serving endpoint. If "
     "deploying to a Databricks app, include a serving endpoint resource named "
     "'serving_endpoint' with CAN_QUERY permissions, as described in "
     "https://docs.databricks.com/aws/en/generative-ai/agent-framework/chat-app#deploy-the-databricks-app")

# Function to check if the endpoint is supported
def is_endpoint_supported(endpoint_name):
    try:
        endpoint = client.serving_endpoints.get(endpoint_name)
        return endpoint is not None
    except Exception as e:
        print(f"Error checking endpoint: {e}")
        return False

# Check if the endpoint is supported
endpoint_supported = is_endpoint_supported(SERVING_ENDPOINT)
if endpoint_supported:
    print(f"Endpoint '{SERVING_ENDPOINT}' is supported.")
else:
    print(f"Endpoint '{SERVING_ENDPOINT}' is not supported.")

def get_user_info():
    headers = st.context.headers
    return dict(
        user_name=headers.get("X-Forwarded-Preferred-Username"),
        user_email=headers.get("X-Forwarded-Email"),
        user_id=headers.get("X-Forwarded-User"),
    )

user_info = get_user_info()

# Streamlit app
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

st.title("🧱 Chatbot App")

# Check if endpoint is supported and show appropriate UI
if not endpoint_supported:
    st.error("⚠️ Unsupported Endpoint Type")
    st.markdown(
        f"The endpoint `{SERVING_ENDPOINT}` is not compatible with this basic chatbot template.\n\n"
        "This template only supports chat completions-compatible endpoints.\n\n"
        "👉 **For a richer chatbot template** that supports all conversational endpoints on Databricks, "
        "please see the [Databricks documentation](https://docs.databricks.com/aws/en/generative-ai/agent-framework/chat-app)."
    )
else:
    st.markdown(
        "ℹ️ This is a simple example. See "
        "[Databricks docs](https://docs.databricks.com/aws/en/generative-ai/agent-framework/chat-app) "
        "for a more comprehensive example with streaming output and more."
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            # Query the Databricks serving endpoint
            assistant_response = query_endpoint(
                endpoint_name=SERVING_ENDPOINT,
                messages=st.session_state.messages,
                max_tokens=400,
            )["content"]
            st.markdown(assistant_response)


        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})