# PowerBI Workspace Migration to Fabric Capacity using Fabric Python SDK

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
## Architecture

Below is the architecture diagram that outlines the workflow for migrating Power BI workspaces to F Capacity:

![Architecture Diagram](../utilities/architecture-fabric-workspace-migration.png)

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
### 5. Select and Assign Workspaces to Capacities
Select the capacity and workspaces for assignment and assign them accordingly.

```
# Select capacity and workspaces for assignment
if capacities:
    selected_capacity_id = input("Enter Capacity ID to assign workspaces to: ")

    print("Select workspaces to assign (comma-separated IDs):")
    for workspace in workspaces:
        print(f"ID: {workspace['id']}, Name: {workspace['displayName']}, Description: {workspace['description']}, Capacity ID: {workspace.get('capacityId', 'N/A')}")
    selected_workspace_ids = input("Enter Workspace IDs: ").split(",")

    # Assign workspaces to the selected capacity
    for workspace_id in selected_workspace_ids:
        assign_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/assignToCapacity"
        data = {"capacityId": selected_capacity_id}
        assign_response = requests.post(assign_url, headers=headers, json=data)

        if assign_response.status_code in [200, 202]:
            print(f"Workspace {workspace_id} assigned successfully to capacity {selected_capacity_id}.")
        else:
            print(f"Failed to assign workspace {workspace_id}: {assign_response.status_code} {assign_response.text}")
else:
    print("No capacities available to select.")
```

### Optional: Map Workspaces to New Capacities
Second option allows you to define the mapping from legacy capacities to new Fabric capacities using capacity IDs and display the mappings, so you can swap capacities at scale.

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
