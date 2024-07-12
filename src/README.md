# Copilot application that implements RAG

This is a sample copilot that application that implements RAG via custom Python code, and can be used with the Azure AI Studio. This sample aims to provide a starting point for an enterprise copilot grounded in custom data that you can further customize to add additional intelligence or capabilities.  

Following the below steps, you will: set up your development environment, create or reference your Azure AI resources, explore prompts, build an index containing product information, run your copilot, evaluate it, and deploy your copilot to a managed endpoint.

> [!IMPORTANT]
> We do not guarantee the quality of responses produced by these samples or their suitability for use in your scenarios, and responses will vary as development of the samples is ongoing. You must perform your own validation the outputs of the application and its suitability for use within your company.


## Step 1: Az login
If you haven't already done so, run `az login` to authenticate to Azure in your terminal.
    - Note: if you are running from within a Codespace or the curated VS Code cloud container, you will need to use `az login --use-device-code`


## Step 2: Reference Azure AI resources
Based on the instructions [here](https://microsoft-my.sharepoint.com/:w:/p/mesameki/Ed5UKepTDSpCpUCwigrxFrsBKMBZrEugqhSrosnz8jtdZQ?e=cudeiv), you already have everything you need. Navigate to your hub and project, click on "Settings" from the left menu, scroll down to "Connected Resource" and click on "View all". We need the information here to fill some of the details of our yaml file below. Open your ./provisioning/provision.yaml file and let's fill it together step by step:

### For the section under "ai":

Under your AI Studio project's "Settings" tab, there is a section called "Project properties". Copy paste all the info you need from there into this part of the yaml file. Note that:
- "hub_name": copy paste what you see under "hub resource name" in the UI 
- "project_name"= The string under field "Name" in the UI

### For the section under "aoai":
Click on "Settings" from the left menu of Azure AI Studio, scroll down to "Connected Resource" and click on "View all". Click on the table row whose type is "Azure OpenAI". Once opened:

- aoai_resource_name: What comes under "Resource" in your table
- kind: "OpenAI" (keep it as is)
- connection_name: Title of the page (written above "Connection Details")
### For the section under "deployments":

Click on the "Deployments" tab from the left menu of Azure AI Studio. If you followed all the steps in the workshop guide doc, you already have two deployments here. One embedding model and one GPT model. Insert information from that table here (the table has column headers name, model name, and version. Exactly what you will use here):

- name: from your Deployments table, copy what is under "name". Example: "gpt-4" 

  model: from your Deployments table, copy what is under "model name". Example: "gpt-4"

  version: from your Deployments table, copy what is under "Model version". Example: 1106.
  
  Repeat this for your embedding model:

- name: from your Deployments table, copy what is under "name"/ Example: "text-embedding-ada-002"
  
  model: from your Deployments table, copy what is under "model name". Example: "gpt-4""text-embedding-ada-002"

  version: from your Deployments table, copy what is under "Model version". Example: "2" # if you don't know, comment this line and we'll pick default
### For the section under "search":
Click on "Settings" from the left menu of Azure AI Studio, scroll down to "Connected Resource" and click on "View all". Click on the table row whose type is "Azure AI Search (Cognitive Search)". Once opened:

- search_resource_name: What comes under "Resource" in your table
- connection_name: Title of the page (written above "Connection Details")


Once you set up those parameters, run:

    ```bash
    # Note: make sure you run this command from the src/ directory so that your .env is written to the correct location (src/)
    cd src
    python provisioning/provision.py --export-env .env

    ```

The script will check whether the resources you specified exist, otherwise it will create them. It will then construct a .env for you that references the provisioned or referenced resources, including your keys. Once the provisioning is complete, you'll be ready to move to step 3.

## Step 3: Create an index

Our goal is to ground the LLM in our custom data (located in src > indexing > data > product-info). To do this, we will use promptflow to create a search index based on the specified product data.

### Step 3a: Create a new index

This step uses vector search with Azure OpenAI embeddings (e.g., ada-002) to encode your documents. First, you need to allow your Azure AI Search resource to access your Azure OpenAI resource in these roles:

    - Cognitive Services OpenAI Contributor
    - Cognitive Services Contributor
    - (optionally if you need quota view) Cognitive Services Usages Reader
 
Follow instructions on https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/role-based-access-control to add role assignment in your Azure OpenAI resource.

Next, run the following script designed to streamline index creation. It builds the search index locally, and publishes it to your AI Studio project in the cloud.

``` bash
python -m indexing.build_index --index-name <desired_index_name> --path-to-data=indexing/data/product-info
```

You can view and use the index you just created on the **Indexes** page of your Azure AI Studio project.

### Step 3b: Set the index reference

NOTE: **Once you have the index you want to use, add the below entry to your .env file.** Note that the copilot code relies on this environment variable.

``` text
AZUREAI_SEARCH_INDEX_NAME=<index-name>
```


## Step 4: Run the copilot

Navigate to the src/flows/rag_copilot_flow directory and open the "flow.dag.yaml" file.  Open the "Visual Editor" in the top left corner of the YAML file.

### Step 4a: Create the flow connections

Open the Promptflow VSCode extension and navigate to the "Extensions" tab.
- Click the Create button ("+") next the "Azure OpenAI" connection option.
  - Fill in the following fields:
    - name: "Default_AzureOpenAI"
    - api_base: "to_replace_with_azure_openai_api_endpoint" <-- Replace with your Azure OpenAI endpoint ex: "https://foo.openai.azure.com/"
  - Click "create connection" near bottom of the file.
    - In the terminal, paste the "api_key" from the Azure OpenAI connection details to securely store the key in your environment.

- Click the Create button ("+") next the "Azure Search" connection option.
  - Fill in the following fields:
    - name: "Default_AzureSearch"
    - api_base: "to_replace_with_azure_search_api_endpoint" <-- Replace with your Azure Search endpoint ex: "https://bar.search.windows.net"
    - Click "create connection" near bottom of the file.
    - In the terminal, paste the "api_key" from the Azure OpenAI connection details to securely store the key in your environment.

### Step 4b: Setup the flow connections

- Open the Visual Editor in the top left corner of the YAML file.
- Select the "DetermineIntent" step and click the "Edit" button.
  - Select the "Default_AzureOpenAI" connection you created in the previous step.
  - Select the "chat" api
  - Enter the desired model in the "Deployment" field.
- Select the "RetrieveDocuments" step and click the "Edit" button.
  - Select the "AzureSearch" connection you created in the previous step.
  - Enter the "index_name" of your search index.
  - Select the "Default_AzureOpenAI" connection you created in the previous step.
  - Enter the "embedding_model" of Azure OpenAI deployment.
- Select the "DetermineReply" step and click the "Edit" button.
  - Select the "Default_AzureOpenAI" connection you created in the previous step.
  - Select the "chat" api
  - Enter the desired model in the "Deployment" field.

### Step 4c: Run the copilot
- Enter a question related to your search index in the "query" field.
- Click the "Run" button in the top right corner of the Visual Editor.