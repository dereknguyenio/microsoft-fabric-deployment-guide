import requests
from msal import ConfidentialClientApplication

# Azure AD app registration details (Replace with your Azure AD App registration details)
client_id = "<YOUR_CLIENT_ID>"  # Placeholder for Azure AD client ID
client_secret = "<YOUR_CLIENT_SECRET>"  # Placeholder for Azure AD client secret
tenant_id = "<YOUR_TENANT_ID>"  # Placeholder for Azure AD tenant ID
authority = f"https://login.microsoftonline.com/{tenant_id}"

# Scopes for Fabric API (Ensure API permissions are granted to this scope)
scopes = ["https://api.fabric.microsoft.com/.default"]

# Create a confidential client application instance
app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# Acquire an access token
result = app.acquire_token_for_client(scopes)

if 'access_token' in result:
    access_token = result['access_token']
    print("Access Token Acquired")

    # Define the function to create a shortcut
    def create_shortcut(workspace_id, item_id, path, name, location, subpath, connection_id):
        """
        Creates a shortcut in the specified workspace and item using the Fabric API.

        :param workspace_id: The ID of the Fabric workspace (Replace with your workspace ID)
        :param item_id: The ID of the target item in the workspace (Replace with your item ID)
        :param path: The path in the Fabric workspace where the shortcut will be created (e.g., "Tables/")
        :param name: The name of the shortcut to be created
        :param location: The URL of the Azure Data Lake Storage (ADLS) Gen2 account
        :param subpath: The subpath within the ADLS Gen2 account pointing to the data
        :param connection_id: The ID of the connection configuration (Replace with your connection ID)
        """
        # Endpoint for creating a shortcut in the Fabric API
        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{item_id}/shortcuts"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        shortcut_data = {
            "path": path,
            "name": name,
            "target": {
                "adlsGen2": {
                    "location": location,
                    "subpath": subpath,
                    "connectionId": connection_id
                }
            }
        }
        
        try:
            # POST request to create the shortcut
            response = requests.post(url, json=shortcut_data, headers=headers)
            
            if 200 <= response.status_code < 300:
                print("Shortcut created successfully:", response.json())
            else:
                print(f"Failed to create shortcut. Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    # Example usage - Replace placeholders with actual values
    create_shortcut(
        workspace_id="<YOUR_WORKSPACE_ID>",  # Placeholder for your Fabric workspace ID
        item_id="<YOUR_ITEM_ID>",            # Placeholder for the target item ID in the workspace. This is your Lakehouse Item ID where your shortcut will land
        path="Tables/",                      # Path in Fabric workspace where the shortcut will be created
        name="prices_delta",                 # Name of the shortcut to be created
        location="<YOUR_ADLS_ACCOUNT_URL>",  # Placeholder for Azure Data Lake Storage (ADLS) Gen2 account URL
        subpath="/gold/stockmarket/prices_delta",  # Subpath within ADLS Gen2 pointing to the data
        connection_id="<YOUR_CONNECTION_ID>"  # Placeholder for the connection configuration ID
    )
else:
    # Error handling for token acquisition failure
    print("Failed to acquire token:", result.get("error"), result.get("error_description"))
