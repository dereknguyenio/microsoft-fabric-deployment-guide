# Workspace Migration to F Capacity

This notebook provides a step-by-step guide to migrating Power BI workspaces to F Capacity based on Capacity and Workspace IDs.

## Prerequisites

Ensure you have the following prerequisites before running the notebook:

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

### 4. Retrieve Capacities and Workspaces
Get the list of capacities and workspaces from the Microsoft Fabric API.

```
import requests

headers = {'Authorization': 'Bearer ' + access_token}

capacities_url = "https://api.fabric.microsoft.com/v1/capacities"
capacities_response = requests.get(capacities_url, headers=headers)
capacities = capacities_response.json()["value"] if capacities_response.status_code == 200 else []

workspaces_url = "https://api.fabric.microsoft.com/v1/workspaces"
workspaces_response = requests.get(workspaces_url, headers=headers)
workspaces = workspaces_response.json()["value"] if workspaces_response.status_code == 200 else []
```
### 5. Map Workspaces to New Capacities
Define the mapping from legacy capacities to new Fabric capacities using capacity IDs and display the mappings.

```
capacity_mapping = {
    "2e931b9d-dbbf-41b9-5555-3333333333": "e1be100d-d431-47cf-8889-4444444444"
    # Add more mappings as needed
}

mappings = []
for workspace in workspaces:
    workspace_name = workspace.get("displayName")
    legacy_capacity_id = workspace.get("capacityId")
    new_capacity_id = capacity_mapping.get(legacy_capacity_id)

    if new_capacity_id:
        mappings.append((workspace_name, workspace['id'], legacy_capacity_id, new_capacity_id))

# Display the mappings
if mappings:
    print("Workspaces and their mapped capacities:")
    for mapping in mappings:
        print(f"Workspace: {mapping[0]} (ID: {mapping[1]})")
        print(f"  Legacy Capacity ID: {mapping[2]}")
        print(f"  New Capacity ID: {mapping[3]}")
        print("  --------")
```
### 6. Migrate Workspaces
Confirm the mappings and proceed with the migration of workspaces to the new capacities.

```
confirm = input("Do you want to proceed with the migration? (yes/no): ").strip().lower()
if confirm != 'yes':
    print("Migration aborted by user.")
    exit()

for mapping in mappings:
    workspace_name, workspace_id, legacy_capacity_id, new_capacity_id = mapping
    assign_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/assignToCapacity"
    data = {"capacityId": new_capacity_id}
    assign_response = requests.post(assign_url, headers=headers, json=data)

    if assign_response.status_code == 200:
        print(f"Workspace {workspace_name} (ID: {workspace_id}) assigned successfully to new capacity (ID: {new_capacity_id}).")
    else:
        print(f"Failed to assign workspace {workspace_name} (ID: {workspace_id}): {assign_response.status_code} {assign_response.text}")

    # Optional: Delay between migrations to manage load
    time.sleep(1)
```

### Notes
Ensure that the capacity mappings are correctly defined.
The script includes debugging prints to help verify each step.
The time.sleep(1) function call can be adjusted or removed based on the load and performance requirements.

### License
This project is licensed under the MIT License.
