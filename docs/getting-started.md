# Microsoft Fabric Deployment Guide

## Getting Started with the Fabric API

This document provides a comprehensive, step-by-step guide to getting started with the Fabric API, including detailed instructions and best practices for successful implementation. This guide will focus on migrating Power BI workspaces to Fabric Capacity using the Fabric API in Python.

### Prerequisites

Ensure you have the following prerequisites before proceeding:

1. **Python Packages**: 
   - Install the required Python packages:
     ```bash
     pip install msal
     pip install azure-identity azure-keyvault-secrets
     ```

2. **Azure Credentials**:
   - Set the following environment variables with your Azure credentials:
     - `AZURE_CLIENT_ID`
     - `AZURE_TENANT_ID`
     - `AZURE_CLIENT_SECRET`

3. **Azure Key Vault**:
   - Your Azure Key Vault should store the client secret needed for authentication.
   - Set the Key Vault name and secret name in the notebook.
  
4. **API Permissions**:
   - Ensure the app registration has the necessary permissions to interact with the Fabric API. Follow these steps:
     1. Go to the [Azure portal](https://portal.azure.com/).
     2. Navigate to "Azure Active Directory" > "App registrations".
     3. Select your app registration (e.g., `Fabric POC App`).
     4. Go to "API permissions" > "Add a permission".
     5. Select "Microsoft Graph" and add the following Delegated permissions:
        - `User.Read`
     6. Select "APIs my organization uses" > "Power BI Service" and add the following Delegated permissions:
        - `Capacity.ReadWrite.All`
        - `Workspace.ReadWrite.All`
   - Grant admin consent for the permissions.

   [Click here to learn more about how to create an App Registration](https://learn.microsoft.com/en-us/rest/api/fabric/articles/get-started/fabric-api-quickstart#create-app-registration)

5. **Workspace Access**:
   - Assign the app registration to the Fabric workspace to have access to the artifacts within the workspace:
     1. Navigate to the workspace.
     2. Click on `Manage access`.
     3. Add the app registration (e.g., `Fabric POC App`) and assign the appropriate role (Admin, Contributor, or Member required).

## Steps

### 1. Set Environment Variables
Set the environment variables for `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET`.

```python
import os

os.environ['AZURE_CLIENT_ID'] = '<CLIENT ID>'
os.environ['AZURE_TENANT_ID'] = '<TENANT ID>'
os.environ['AZURE_CLIENT_SECRET'] = '<CLIENT SECRET>'
```

### 2. Retrieve Client Secret from Azure Key Vault
Fetch the client secret from Azure Key Vault using the azure-identity and azure-keyvault-secrets packages.

```
from azure.identity import EnvironmentCredential
from azure.keyvault.secrets import SecretClient

key_vault_name = "<KEY_VAULT_NAME>"
secret_name = "<KEY_VAULT_SECRET>"
vault_url = f"https://{key_vault_name}.vault.azure.net"
credential = EnvironmentCredential()
secret_client = SecretClient(vault_url=vault_url, credential=credential)

retrieved_secret = secret_client.get_secret(secret_name)
client_secret = retrieved_secret.value
```
### 3. Acquire Token for Microsoft Fabric API
Use the msal package to acquire an access token for the Microsoft Fabric API.

```
from msal import ConfidentialClientApplication

tenant_id = os.getenv('AZURE_TENANT_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["https://api.fabric.microsoft.com/.default"]

app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
result = app.acquire_token_for_client(scopes)

if 'access_token' in result:
    access_token = result['access_token']
else:
    raise Exception("Token acquisition failed:", result.get("error"), result.get("error_description"))

```
### Making API Requests

You can interact with various endpoints provided by the Fabric API. Below are examples of common operations:

#### Example 1: Retrieve Capacities

```python
import requests

headers = {'Authorization': 'Bearer ' + access_token}

capacities_url = "https://api.fabric.microsoft.com/v1/capacities"
capacities_response = requests.get(capacities_url, headers=headers)
if capacities_response.status_code == 200:
    capacities = capacities_response.json()["value"]
    for capacity in capacities:
        print(f"ID: {capacity['id']}, Name: {capacity['displayName']}")
else:
    print("Failed to retrieve capacities:", capacities_response.status_code, capacities_response.text)
```

#### Example 2: List Workspaces

```
workspaces_url = "https://api.fabric.microsoft.com/v1/workspaces"
workspaces_response = requests.get(workspaces_url, headers=headers)
if workspaces_response.status_code == 200:
    workspaces = workspaces_response.json()["value"]
    for workspace in workspaces:
        print(f"ID: {workspace['id']}, Name: {workspace['displayName']}")
else:
    print("Failed to retrieve workspaces:", workspaces_response.status_code, workspaces_response.text)
```

#### Example 3: Assign Workspace to Capacity

```
workspace_id = "<WORKSPACE_ID>"
capacity_id = "<CAPACITY_ID>"
assign_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/assignToCapacity"
data = {"capacityId": capacity_id}
assign_response = requests.post(assign_url, headers=headers, json=data)

if assign_response.status_code in [200, 202]:
    print(f"Workspace {workspace_id} assigned successfully to capacity {capacity_id}.")
else:
    print(f"Failed to assign workspace {workspace_id}: {assign_response.status_code} {assign_response.text}")
```

### Error Handling
Implement robust error handling to manage API errors gracefully.
```
def handle_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None
```

### Conclusion
By following this guide, you can start using the Fabric API to automate and integrate Microsoft Fabric with your existing systems. Refer to the official API documentation for detailed information on all available endpoints and their usage.

For further assistance, consult the Microsoft Fabric documentation and community forums.
