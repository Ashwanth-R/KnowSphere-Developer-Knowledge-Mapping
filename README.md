# KnowSphere-Developer-Knowledge-Mapping

## Overview

KnowSphere-Developer-Knowledge-Mapping is an AI-powered developer assistant and knowledge mapping platform designed for teams and organizations. Built for the AWS Lambda Hackathon, this project leverages serverless architecture, Streamlit UI to visualize, and interact with developer knowledge, domain expertise, and contributor data.

## Features

- **Conversational Chatbot UI:**
  - Intuitive chat interface built with Streamlit for seamless Q&A about developers, domains, and contributors.
  - Real-time responses powered by a backend API (deployed on AWS Lambda).

- **Knowledge Mapping:**
  - Maps relationships between developers, domains, and contributions.
  - Enables discovery of expertise, project history, and domain knowledge within an organization.

- **Serverless & Scalable:**
  - Backend API is deployed on AWS Lambda for cost-effective, scalable, and event-driven operation.
  - Easily extensible to integrate with other AWS services (DynamoDB, S3, etc.).

- **Customizable Themes:**
  - Multiple UI themes for a personalized experience.

- **Modern UI/UX:**
  - Responsive, accessible, and visually appealing chat interface.
  - Clean separation of logic and styles (CSS).

## Architecture
![image](https://github.com/user-attachments/assets/f8d753d7-fdb7-4fb6-bbe0-4318ccafe9ce)

```
User (Streamlit UI) <-> API Gateway <-> AWS Lambda (Backend) <-> Data Sources (DB, Files, etc.)
```

- **Frontend:** Streamlit app (`chatbot_ui.py`, `chatbot.py`) for chat and visualization.
- **Backend:** Python-based AWS Lambda function, exposed via API Gateway.
- **Styling:** Custom CSS for chat bubbles, themes, and layout.

## Getting Started

### Prerequisites
- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [AWS CLI](https://aws.amazon.com/cli/) (for deployment)
- AWS account (for Lambda/API Gateway)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/KnowSphere-Developer-Knowledge-Mapping.git
   cd KnowSphere-Developer-Knowledge-Mapping
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file with your API Gateway URL:
     ```
     API_GATEWAY_URL=https://your-api-gateway-url.amazonaws.com/prod/endpoint
     ```

### Running Locally
```bash
streamlit run chatbot_ui.py
```

### Deploying Backend

The backend consists of AWS Lambda functions that handle the core logic for knowledge mapping and developer queries. The Lambda functions are organized in the `backend/lambda` folder structure.

#### Backend Architecture Details

The backend consists of specialized Lambda functions that analyze different data sources to build a comprehensive knowledge map:

- **Chat Handler:** `upload_db_to_s3.py` serves as the orchestrator that processes incoming requests from the API Gateway and coordinates with other specialized analyzers.

- **GitHub Analyzer (`github_analyzer`):**
  - Analyzes GitHub repositories, commits, pull requests, and issues
  - Extracts developer contributions, code expertise areas, and collaboration patterns
  - Identifies domain knowledge based on repository topics, file types, and commit messages
  - Maps relationships between contributors and their technical specializations

- **Jira Analyzer (`jira_analyzer`):**
  - Processes Jira tickets, epics, and project data
  - Identifies developer involvement in different business domains and project areas
  - Analyzes issue resolution patterns and developer expertise in specific problem domains
  - Tracks feature development lifecycle and contributor involvement

- **Confluence Analyzer (`confluence_analyzer`):**
  - Processes documentation, meeting notes, and knowledge base articles
  - Extracts subject matter expertise from authored content
  - Identifies domain knowledge leaders and documentation contributors
  - Maps relationships between documented processes and responsible team members

- **Serverless Execution:** Each analyzer runs independently as Lambda functions, ensuring cost-effective scaling based on demand and data source availability.

#### Deployment Steps

1. **Package Lambda Function:**
   ```bash
   cd backend/lambda
   zip -r lambda_function.zip .
   ```

2. **Deploy using AWS CLI:**
   ```bash
   aws lambda create-function \
     --function-name knowsphere-dev-assistant \
     --zip-file fileb://lambda_function.zip \
     --handler export_more_granular.lambda_handler \
     --runtime python3.9 \
     --role arn:aws:iam::your-account:role/lambda-execution-role
   ```

3. **Set up API Gateway:**
   - Create a REST API in AWS API Gateway
   - Create a resource and method (POST)
   - Integrate with your Lambda function
   - Deploy the API and note the endpoint URL

4. **Update Environment Variables:**
   - Update the `.env` file with your API Gateway URL
   - Configure any required AWS credentials or IAM roles

#### Lambda Function Execution Flow

1. **Request Reception:** API Gateway receives HTTP requests from the Streamlit frontend
2. **Lambda Invocation:** Gateway triggers the Lambda function with the request payload
3. **Data Processing:** Lambda function processes the query using:
   - **GitHub Analysis:** Scans repositories for code contributions, language expertise, and collaboration networks
   - **Jira Integration:** Analyzes ticket assignments, project involvement, and domain-specific problem-solving patterns  
   - **Confluence Processing:** Extracts knowledge from documentation, meeting notes, and authored content
   - **Context-aware response generation:** Synthesizes information to provide comprehensive answers
4. **Response Generation:** Function returns structured JSON response with:
   - Processed answer to the user query
   - Confidence scores and metadata
   - Related suggestions or follow-up questions
5. **Response Delivery:** API Gateway returns the response to the frontend for display

#### Individual Lambda Function Details

**GitHub Analyzer (`github_analyzer.py`):**
- **Purpose:** Extracts developer expertise from GitHub activity
- **Data Sources:** Repositories, commits, pull requests, issues, code reviews
- **Key Metrics:** Lines of code, programming languages, project involvement, collaboration frequency
- **Output:** Developer skill profiles, technology expertise maps, collaboration networks

**Jira Analyzer (`jira_analyzer.py`):**
- **Purpose:** Maps business domain expertise from project management data
- **Data Sources:** Jira tickets, epics, sprints, project assignments
- **Key Metrics:** Issue resolution times, domain-specific involvement, project leadership roles
- **Output:** Business domain expertise, problem-solving capabilities, project contribution history

**Confluence Analyzer (`confluence_analyzer.py`):**
- **Purpose:** Identifies knowledge sharing and documentation expertise
- **Data Sources:** Pages, blog posts, comments, space ownership
- **Key Metrics:** Content authorship, knowledge domain coverage, documentation quality
- **Output:** Subject matter expertise, knowledge sharing patterns, documentation leadership

## File Structure

```
KnowSphere-Developer-Knowledge-Mapping/
├── backend/
│   └── lambda/
│       ├── chat_handler
│       ├── github_analyzer
│       ├── jira_analyzer
│       ├── confluence_analyzer
│       └── dev_domain_map
│   └── utils/
        └── upload_db_to_s3
├── chatbot_ui.py
├── requirements.txt                 
├── style.css                       
└── README.md                       
```

## Acknowledgements

- Built for the AWS Lambda Hackathon.
- Powered by Streamlit, AWS Lambda, and open-source Python libraries.

---

For questions or support, please open an issue on GitHub.
