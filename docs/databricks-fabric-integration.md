## End-to-End Flow: Databricks + Fabric + Azure Data Factory Architecture

This end-to-end guide outlines the complete data flow and configuration steps required to set up an architecture that integrates Azure Databricks, Microsoft Fabric, and Azure Data Factory (ADF).

### 1. Set Up and Configure Service Principals (SPs)

- **Create Service Principal in Azure Active Directory (Entra ID):**
  - Navigate to Entra ID and create a Service Principal named "Fabric SP POC DKN."
  - Assign the necessary API permissions to the SP to interact with Databricks, Azure Data Lake Storage (ADLS) Gen2, and Microsoft Fabric.

- **Store SP Credentials in Azure Key Vault:**
  - Create an Azure Key Vault to securely store the Service Principal's credentials.
  - Ensure that Databricks and ADF have access permissions to retrieve secrets from the Key Vault.

### 2. Configure Azure Databricks

- **Set Up Databricks Workspace:**
  - Create and configure a Databricks workspace in Azure, setting up access controls and assigning the admin group.

- **Create Secret Scope in Databricks:**
  - In Databricks, create a Secret Scope backed by the Azure Key Vault. This allows secure access to the stored Service Principal credentials. 
  - [Example for Creating Secret Scope](https://<your-databricks-instance-url>/?o=<workspace-id>#secrets/createScope).

- **Mount ADLS Gen2 Containers:**
  - Use the credentials from the Key Vault to mount the Bronze, Silver, and Gold containers in ADLS Gen2 within Databricks. This setup allows Databricks to securely read from and write to the ADLS Gen2 containers.

  ```python
  # ADLS Mount
  service_credential = dbutils.secrets.get(scope="key-vault-secret-scope", key="databricks-sp-secret")

  spark.conf.set("fs.azure.account.auth.type.<storage-account-name>.dfs.core.windows.net", "OAuth")
  spark.conf.set("fs.azure.account.oauth.provider.type.<storage-account-name>.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
  spark.conf.set("fs.azure.account.oauth2.client.id.<storage-account-name>.dfs.core.windows.net", "<your-client-id>")
  spark.conf.set("fs.azure.account.oauth2.client.secret.<storage-account-name>.dfs.core.windows.net", service_credential)
  spark.conf.set("fs.azure.account.oauth2.client.endpoint.<storage-account-name>.dfs.core.windows.net", "https://login.microsoftonline.com/<your-tenant-id>/oauth2/token")

  # Fabric OneLake Mount
  service_credential = dbutils.secrets.get(scope="key-vault-dkn-secret-scope", key="databrickssptofabric-v2-deltalakeinday")

  spark.conf.set("fs.azure.account.auth.type.onelake.dfs.fabric.microsoft.com", "OAuth")
  spark.conf.set("fs.azure.account.oauth.provider.type.onelake.dfs.fabric.microsoft.com", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
  spark.conf.set("fs.azure.account.oauth2.client.id.onelake.dfs.fabric.microsoft.com", "<your-client-id>")
  spark.conf.set("fs.azure.account.oauth2.client.secret.onelake.dfs.fabric.microsoft.com", service_credential)
  spark.conf.set("fs.azure.account.oauth2.client.endpoint.onelake.dfs.fabric.microsoft.com", "https://login.microsoftonline.com/<your-tenant-id>/oauth2/token")

  # Path for saving data
  oneLakePath = "abfss://<container-name>@onelake.dfs.fabric.microsoft.com/<folder-path>/Tables/stockprices"
  df_gold.write.format("delta").option("header", "true").mode("overwrite").save(oneLakePath)
