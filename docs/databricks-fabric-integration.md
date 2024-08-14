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
  ```
### 3. Set Up Azure Data Lake Storage (ADLS) Gen2

- **Create Storage Accounts:**
  - Create Azure Data Lake Storage Gen2 accounts with containers for each layer of data processing: Bronze, Silver, and Gold.

- **Set Access Permissions:**
  - Assign appropriate access permissions to allow Databricks and ADF to interact with these containers securely.

  #### Storage Blob Data Contributor Role
  The Storage Blob Data Contributor role is necessary to allow services to read, write, and delete data within the storage account's containers. This role provides the required access for both Azure Data Factory (ADF) and Microsoft Fabric to interact with the data stored in ADLS Gen2.

  **Permissions Granted:**

  - **ADF Managed Identity:**
    - **Role:** Storage Blob Data Contributor
    - **Scope:** Specific to the resource (ADLS Gen2 Storage Account).
    - **Purpose:**
      - Allows ADF to read from and write data to the ADLS Gen2 containers (Bronze, Silver, Gold).
      - Enables ADF pipelines to orchestrate data movement and trigger Databricks jobs that process data within these containers.

  - **Microsoft Fabric App Registration:**
    - **Role:** Storage Blob Data Contributor
    - **Scope:** Specific to the resource (ADLS Gen2 Storage Account).
    - **Purpose:**
      - Provides Microsoft Fabric the ability to access, modify, and store data within the ADLS Gen2 storage layers.
      - Ensures that processed data from Databricks can be synchronized with Fabric’s Lakehouses.

### 4. Set Up Azure Data Factory (ADF) Pipelines

- **Create ADF Pipelines:**
  - In ADF, create data pipelines that manage the flow of data from the Bronze container to Silver and Gold containers.
  - These pipelines will trigger Databricks notebooks or jobs to process the data.

- **Configure Linked Services in ADF:**
  - Set up a linked service in ADF to connect to the Databricks workspace. Use the Managed Identity authentication method to secure the connection.
  - Grant ADF Managed Identity 'Contributor' IAM Role Permissions in Azure Databricks.
  - Additionally, configure linked services for ADLS Gen2 to read and write data as part of the pipeline process.

### 5. Databricks Service Principal Setup

- **Purpose of Service Principals in Databricks:**
  - Service Principals are used to authenticate and authorize automated processes, such as running jobs, interacting with Azure resources, and integrating with other services like Azure Data Factory (ADF).
  - By configuring a Service Principal within Databricks, you ensure that your automated processes have the necessary access to resources, maintaining security and minimizing the risk of unauthorized access.

- **Steps to Set Up and Use a Service Principal in Databricks:**

  - **Create a Service Principal (SP):**
    - Create a Service Principal named "Fabric SP POC" within the Databricks workspace under Identity and access settings.
    - This SP is associated with a unique Application ID (`<your-application-id>`), which is used to identify it when granting permissions.

  - **Granting Permissions to the SP:**
    - Assign specific roles and permissions to this SP within Databricks to allow it to perform actions like running jobs, accessing storage, and interacting with other Azure services.
    - In your setup, the SP is given permissions to manage Databricks resources and interact with ADLS Gen2 storage.

- **Use Case in Architecture:**
  - The "Fabric SP POC" Service Principal would typically be used by ADF pipelines or other automation scripts that interact with Databricks, allowing them to authenticate securely and execute tasks within the Databricks environment.

- **Service Principal Creation in Entra ID:**
  - When you create a Service Principal in Entra ID, you're essentially creating an identity that can be used to authenticate and authorize access to Azure resources. This SP can be used by various Azure services, such as Azure Data Factory (ADF), Azure Storage, and more, to interact securely with other resources within your Azure environment.

- **Configuring the Service Principal in Databricks:**
  - Even though you've created the Service Principal in Entra ID, Databricks, as a platform, needs to recognize and use this identity for specific tasks. By configuring the SP in Databricks, you're essentially telling Databricks to use this particular identity for performing tasks like running jobs, accessing data, and managing resources.

### 6. Data Processing in Databricks

- **Execute Spark Jobs:**
  - Trigger Spark jobs from ADF that perform data processing on raw data stored in the Bronze container.
  - These jobs refine and clean the data, storing the processed results in the Silver container.

- **Final Data Processing to Gold Container:**
  - Further processing steps in Databricks will convert the Silver data into a final, analytics-ready format, which is stored in the Gold container.

### 7. Integration with Microsoft Fabric

- **Set Up Fabric Lakehouses:**
  - Configure Lakehouses in Microsoft Fabric to correspond to the Bronze, Silver, and Gold layers.
  - Ensure that the processed data from Databricks is synchronized with the appropriate Lakehouse layers in Fabric.

- **Use Fabric Capacity:**
  - Allocate and manage resources within Fabric to optimize the storage and processing of data across the Lakehouse layers.

- **Implement Semantic Models and Power BI:**
  - Leverage the semantic models in Fabric to prepare data for reporting and analysis.
  - Connect Power BI to the Gold Lakehouse to visualize the data and generate insights.

### 8. Secure and Monitor the Architecture

- **Assign Roles and Permissions:**
  - Continuously monitor and manage access control across Databricks, ADF, ADLS Gen2, and Fabric to ensure security.
  - Regularly audit the permissions of the Service Principal and Managed Identity to comply with organizational security policies.

- **Monitor ADF Pipeline Execution:**
  - Use ADF’s monitoring tools to track the status of pipeline executions, ensuring they run as expected and troubleshooting any issues that arise.

### 9. Testing and Validation

- **Test the Full Data Flow:**
  - Run test jobs in Databricks to validate the entire data pipeline from ingestion in the Bronze container to final storage in the Gold Lakehouse.
  - Check data integrity and ensure that all steps in the pipeline are functioning as expected.

- **Verify Outputs in Fabric and Power BI:**
  - Confirm that the processed data in Fabric’s Lakehouses is accurate and accessible for further analysis.
  - Use Power BI to visualize the data and validate that it meets business requirements.
