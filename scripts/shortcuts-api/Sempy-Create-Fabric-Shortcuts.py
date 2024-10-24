#https://bradleyschacht.com/working-with-fabric-shortcuts-in-pyspark

import requests
import time
import json
from notebookutils import mssparkutils
import sempy.fabric as fabric

# Function to manage shortcuts using Fabric REST API
def fn_shortcut(action, shortcut_path, shortcut_name, target=None):
    """
    Function to manage shortcuts using the Fabric REST API. Supports Create, Get, and Delete actions.
    
    :param action: The action to perform (Create, Get, or Delete)
    :param shortcut_path: The path to the shortcut parent directory (e.g., "Tables/")
    :param shortcut_name: The name of the shortcut
    :param target: The target configuration (required for Create action)
    """
    
    # Get the workspace ID and lakehouse ID using sempy
    workspace_id = fabric.get_workspace_id()
    lakehouse_id = fabric.get_lakehouse_id()
    
    # Set up the headers and the API URL
    headers = {
        'Authorization': f'Bearer {mssparkutils.credentials.getToken("pbi")}',
        'Content-Type': 'application/json'
    }
    
    if action == 'Get':
        # Get shortcut details
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/shortcuts/{shortcut_path}/{shortcut_name}'
        response = requests.get(url, headers=headers)
        
    elif action == 'Create':
        # Create shortcut with target configuration
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/shortcuts?shortcutConflictPolicy=Abort'
        data = {
            "path": shortcut_path,
            "name": shortcut_name,
            "target": target
        }
        response = requests.post(url, headers=headers, json=data)
        
    elif action == 'Delete':
        # Delete shortcut
        url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/shortcuts/{shortcut_path}/{shortcut_name}'
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            # Wait for the delete operation to fully propagate
            while mssparkutils.fs.exists(f'{shortcut_path}/{shortcut_name}'):
                time.sleep(5)
    
    # Check response status
    if 200 <= response.status_code <= 299:
        response_content = {
            "request_url": response.url,
            "response_content": {} if response.text == '' else json.loads(response.text),
            "status": "success",
            "status_code": response.status_code,
            "status_description": response.reason
        }
    else:
        response_content = {
            "request_body": target,
            "request_url": response.url,
            "response_text": json.loads(response.text),
            "status": "error",
            "status_code": response.status_code,
            "status_description": response.reason
        }
    
    return response_content

def list_folders(base_path):
    """
    List all directories at a given base path using mssparkutils.fs.ls().
    
    :param base_path: The base path where the folders reside
    :return: List of folder names
    """
    try:
        folders = [file_info.name.strip('/') for file_info in mssparkutils.fs.ls(base_path) if file_info.isDir]
        return folders
    except Exception as e:
        print(f"Error listing folders in {base_path}: {e}")
        return []

# Function to create shortcuts for all Delta tables in the Gold layer based on folder names
def create_shortcuts_for_gold_tables():
    base_path = f"abfss://gold@{account_name}.dfs.core.windows.net/deltacopy/wwi/"
    
    # List all schema directories in the Gold layer
    schemas = list_folders(base_path)
    
    for schema in schemas:
        schema_path = f"{base_path}{schema}/"
        
        # List all table directories under each schema
        tables = list_folders(schema_path)
        
        for table_name in tables:
            shortcut_path = f"Tables/"
            
            # ADLS Gen2 target information for the shortcut
            target = {
                "adlsGen2": {
                    "location": f"https://{account_name}.dfs.core.windows.net",
                    "subpath": f"/<CONTAINER>/{schema}/{table_name}",
                    "connectionId": "<CONNECTIONID>"  # Replace with actual connection ID
                }
            }
            
            # Create shortcut
            result = fn_shortcut(action='Create', shortcut_path=shortcut_path, shortcut_name=f"{schema}_{table_name}", target=target)
            print(f"Creating shortcut for {schema}.{table_name}: {result['status']}")

# Run the function to create all shortcuts
create_shortcuts_for_gold_tables()
