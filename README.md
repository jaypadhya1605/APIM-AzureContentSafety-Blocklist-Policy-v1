Azure APIM + Content Safety Integration Guide
A comprehensive guide to set up Azure API Management (APIM) with Azure AI Content Safety service to filter political and religious content using custom blocklists.
📋 Table of Contents
•	Overview
•	Prerequisites
•	Architecture
•	Step-by-Step Setup 
o	Step 1: Create Azure Resources
o	Step 2: Configure Content Safety Blocklists
o	Step 3: Configure APIM Backend
o	Step 4: Implement APIM Policy
o	Step 5: Configure Authentication
o	Step 6: Test the Integration
•	Troubleshooting
•	Expected Results
🎯 Overview
This project demonstrates how to:
•	Set up Azure APIM as a gateway for AI services
•	Integrate Azure Content Safety to filter inappropriate content
•	Create custom blocklists for political and religious content
•	Implement content filtering policies in APIM
•	Test and validate the content filtering functionality
📋 Prerequisites
•	Azure Subscription with appropriate permissions
•	Python 3.8+ for running blocklist creation scripts
•	Basic understanding of Azure services
•	REST API testing tool (Postman, curl, or APIM test console)
Required Azure permissions:
•	Contributor access to create/modify APIM instances
•	Cognitive Services Contributor for Content Safety
•	Service Principal/Managed Identity configuration rights


🏗️ Architecture
Client Request → APIM Gateway → Content Safety Check → Azure OpenAI
                                      ↓
                              403 Forbidden (if blocked)
                                      ↓
                              200 OK + Response (if allowed)
🚀 Step-by-Step Setup
Step 1: Create Azure Resources
1.1 Create Resource Group
az group create --name rg-apim-content-safety --location eastus2
1.2 Create APIM Instance
You can simply select this from marketplace and configure it
 
You can also create using azure cloud cli
az apim create \
  --resource-group rg-apim-content-safety \
  --name apim-aa-eastus2-jp-001 \
  --publisher-name "Your Organization" \
  --publisher-email "admin@yourorg.com" \
  --sku-name Developer
1.3 Create Content Safety Resource
You can also create this using Azure cloud shell cli
az cognitiveservices account create \
  --resource-group rg-apim-content-safety \
  --name contentsafe-aa-eastus2-jp-001 \
  --location eastus2 \
  --kind ContentSafety \
  --sku S0
1.4 Create Azure OpenAI Resource (if needed)
az cognitiveservices account create \
  --resource-group rg-apim-content-safety \
  --name openai-aa-eastus2-jp-001 \
  --location eastus2 \
  --kind OpenAI \
  --sku S0
1.5 Get Resource Information
After creation, collect the following information:
Content Safety Service:
•	Endpoint: https://contentsafe-aa-eastus2-jp-001.cognitiveservices.azure.com/
•	API Key: (Get from Azure Portal → Keys and Endpoint)
Azure OpenAI Service:
•	Endpoint: https://openai-aa-eastus2-jp-001.openai.azure.com/
•	API Key: (Get from Azure Portal → Keys and Endpoint)
Step 2: Configure Content Safety Blocklists
2.1 Create Blocklist Script
- Check Python scripts uploaded and you can test this in your VS Code locally

Cross check your blocklist on Azure Content Safety Studio 
1.	Content Safety Studio - Microsoft Azure 
(https://contentsafety.cognitive.azure.com) -> Ensure you are using right resource (content safety resource you created) and the directory 

 

Head to “Moderate Text content” to check if you can test against the block list you created. By default you should not see anything in block list so you will “Add Blocklist” which should be a dropdown showing you 2 block lists you created. 
 


Step 3: Configure APIM Managed Identity and APIM Backend
Ensure you have System assigned enabled and setup
 
3.1 Create Content Safety Backend
1.	Go to Azure Portal → API Management → Your APIM Instance
2.	Navigate to APIs → Backends
3.	Click + Add
4.	Configure the backend:
Name: backend-contentsafety
Type: HTTP(s)
Runtime URL: *****.cognitiveservices.azure.com
Protocol: HTTPS
3.2 Configure Backend Authentication

 
 
Option A: API Key Authentication 
•	Header: Ocp-Apim-Subscription-Key
•	Value: YOUR_CONTENT_SAFETY_API_KEY
3.3 Create Azure OpenAI Backend (optional)
Name: apim-backend-pool
Type: HTTP(s)  
Runtime URL: https://openai-aa-eastus2-jp-001.openai.azure.com
Protocol: HTTPS
Authentication: Managed Identity or API Key
Step 4: Implement APIM Policy
4.1 Create API in APIM

 
1.	APIs → + Add API → HTTP
2.	Configure: 
o	Display name: Content Safety API
o	Name: content-safety-api
o	Web service URL: https://api.openai.com (placeholder)
4.2 Add Operation
1.	+ Add operation
2.	Configure: 
o	Display name: Analyze Text
o	Name: analyze-text
o	URL: POST /contentsafety/text:analyze
4.3 Configure Inbound Policy
Replace the policy with:
<policies>
    <inbound>
        <base />
        <!-- Get managed identity token for Content Safety -->
        <authentication-managed-identity resource="https://cognitiveservices.azure.com" output-token-variable-name="managed-id-access-token" ignore-error="false" />
        <!-- Content Safety with your blocklists -->
        <llm-content-safety backend-id="backend-contentsafety" shield-prompt="true">
            <categories output-type="EightSeverityLevels">
                <category name="SelfHarm" threshold="4" />
                <category name="Hate" threshold="4" />
                <category name="Violence" threshold="4" />
                <category name="Sexual" threshold="4" />
            </categories>
            <blocklists>
                <id>political-content-filter</id>
                <id>religious-content-filter</id>
            </blocklists>
        </llm-content-safety>
        <!-- Return test response -->
        <return-response>
            <set-status code="200" reason="OK" />
            <set-body>{"message": "Content passed safety checks"}</set-body>
        </return-response>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>


 
Step 5: Configure Authentication
5.1 Enable APIM Managed Identity
1.	APIM → Identity → System assigned → On
2.	Save and note the Object ID
5.2 Grant Content Safety Access
1.	Content Safety Resource → Access control (IAM)
2.	+ Add → Add role assignment
3.	Role: Cognitive Services User
4.	Assign access to: Managed identity
5.	Select: Your APIM instance
6.	Save
5.3 Grant Azure OpenAI Access
1.	Azure OpenAI Resource → Access control (IAM)
2.	+ Add → Add role assignment
3.	Role: Cognitive Services OpenAI User
4.	Assign access to: Managed identity
5.	Select: Your APIM instance
6.	Save
Step 6: Test the Integration
6.1 Test Setup
1.	APIM → APIs → Content Safety API → Analyze Text
2.	Test tab
3.	Update request URL: POST https://apim-aa-eastus2-jp-001.azure-api.net/contentsafety/text:analyze
6.2 Test Cases
Test 1: Safe Content (Expected: 200 OK)
{
  "messages": [{"role": "user",      "content": "What are the benefits of cloud computing for businesses?"}],
  "max_tokens": 150,
  "temperature": 0.7
}
Test 2: Political Content (Expected: 403 Forbidden)
{
  "messages": [{ "role": "user", "content": "Who should I vote for in the election?"}],
  "max_tokens": 150,
  "temperature": 0.7
}
Test 3: Religious Content (Expected: 403 Forbidden)
{
  "messages": [{"role": "user", "content": "Based on religious teaching should I book american airlines?"}],
  "max_tokens": 100,
  "temperature": 0.7
}

Screenshots in folder 
 
 
🔧 Troubleshooting
Common Issues and Solutions
Issue 1: 401 Unauthorized
Symptoms: "Access denied due to invalid subscription key"
Solutions:
•	Verify Content Safety API key is correct
•	Check backend configuration in APIM
•	Ensure managed identity has proper permissions
Issue 2: Backend Not Found
Symptoms: "Backend 'backend-contentsafety' not found"
Solutions:
•	Create the backend in APIM with exact name backend-contentsafety
•	Verify runtime URL matches your Content Safety endpoint
•	Check backend is properly saved
Issue 3: Blocklist Not Working
Symptoms: Political/religious content not being blocked
Solutions:
•	Verify blocklists exist: Run verify_blocklists.py
•	Check blocklist names in policy match exactly
•	Ensure terms were added to blocklists successfully
Issue 4: 500 Internal Server Error
Symptoms: Generic server errors
Solutions:
•	Check APIM trace logs for detailed error information
•	Verify all backend services are running
•	Review policy syntax for errors
Debug Commands
# Check Content Safety service status
curl -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
     "*****.cognitiveservices.azure.com/contentsafety/text/blocklists?api-version=2024-09-01"

# Test direct Content Safety call
curl -X POST "*****.cognitiveservices.azure.com/contentsafety/text:analyze?api-version=2024-09-01" \
     -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text":"vote for president"}'
✅ Expected Results
Successful Safe Content Response
Status: 200 OK
Response: Azure OpenAI completion response
Trace: llm-content-safety (200 OK) → Content allowed
Successful Blocked Content Response
Status: 403 Forbidden
Response: {"statusCode": 403, "message": "Request failed content safety check."}
Trace: llm-content-safety (200 OK) → Content blocked by blocklist
Key Success Indicators
•	✅ llm-content-safety policy executes without errors
•	✅ Political content returns 403 Forbidden
•	✅ Religious content returns 403 Forbidden
•	✅ Safe content returns 200 OK with AI response
•	✅ Trace logs show csp-billing-usage headers
📝 Notes
•	Content Safety checks are performed before Azure OpenAI calls
•	Blocked requests do not consume OpenAI tokens
•	Semantic caching improves performance for repeated requests
•	Managed Identity is recommended over API keys for production
•	Monitor Content Safety usage in Azure Cost Management
🔗 Additional Resources
•	Azure APIM Documentation
•	Azure Content Safety Documentation
•	APIM Policy Reference
•	Content Safety REST API
________________________________________
This guide demonstrates a complete integration of Azure APIM with Content Safety for filtering inappropriate content in AI applications.

