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
