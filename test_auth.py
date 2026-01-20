from databricks.sdk import WorkspaceClient

try:
    # Attempt to initialize the WorkspaceClient
    client = WorkspaceClient()
    print("Authentication successful!")
except Exception as e:
    # Print the error if authentication fails
    print(f"Authentication failed: {e}")