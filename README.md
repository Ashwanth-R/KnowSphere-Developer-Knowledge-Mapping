# KnowSphere-Developer-Knowledge-Mapping

## Overview

KnowSphere-Developer-Knowledge-Mapping is an AI-powered developer assistant and knowledge mapping platform designed for teams and organizations. Built for the AWS Lambda Hackathon, this project leverages serverless architecture, Streamlit UI, and modern NLP techniques to help users query, visualize, and interact with developer knowledge, domain expertise, and contributor data.

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
or
```bash
streamlit run chatbot.py
```

### Deploying Backend

The backend consists of AWS Lambda functions that handle the core logic for knowledge mapping and developer queries. The Lambda functions are organized in the `backend/lambda` folder structure.

#### Backend Architecture Details

The backend consists of specialized Lambda functions that analyze different data sources to build a comprehensive knowledge map:

- **Main Lambda Handler:** `export_more_granular.py` serves as the orchestrator that processes incoming requests from the API Gateway and coordinates with other specialized analyzers.

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

- **Knowledge Integration:** All analyzers feed into a unified knowledge graph that correlates data across platforms to provide comprehensive developer insights.

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
   - **Natural Language Processing:** Combines insights from all sources for intent recognition and context understanding
   - **Knowledge graph traversal:** Finds relevant connections between developers, domains, and contributions
   - **Context-aware response generation:** Synthesizes information to provide comprehensive answers
4. **Response Generation:** Function returns structured JSON response with:
   - Processed answer to the user query
   - Confidence scores and metadata
   - Related suggestions or follow-up questions
5. **Response Delivery:** API Gateway returns the response to the frontend for display

#### Lambda Environment Configuration

- **Memory:** 512MB - 1GB (adjustable based on data size)
- **Timeout:** 30 seconds (sufficient for most queries)
- **Runtime:** Python 3.9+
- **Environment Variables:**
  - `LOG_LEVEL`: For debugging purposes
  - `DATA_SOURCE`: Configuration for data storage location
  - `GITHUB_TOKEN`: GitHub API authentication token
  - `JIRA_BASE_URL`: Jira instance URL
  - `JIRA_USERNAME`: Jira authentication username
  - `JIRA_API_TOKEN`: Jira API token
  - `CONFLUENCE_BASE_URL`: Confluence instance URL
  - `CONFLUENCE_USERNAME`: Confluence authentication username
  - `CONFLUENCE_API_TOKEN`: Confluence API token

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
│       ├── export_more_granular.py    # Main Lambda handler and orchestrator
│       ├── github_analyzer.py         # GitHub repository and contribution analysis
│       ├── jira_analyzer.py          # Jira ticket and project analysis
│       ├── confluence_analyzer.py    # Confluence documentation analysis
│       ├── knowledge_processor.py    # Core knowledge processing and graph logic
│       ├── nlp_utils.py             # NLP utilities and text processing helpers
│       └── requirements.txt         # Lambda-specific dependencies
├── chatbot_ui.py                    # Main Streamlit UI with advanced features
├── chatbot.py                       # Minimal Streamlit chatbot UI
├── requirements.txt                 # Frontend Python dependencies
├── style.css                        # Main UI styles
├── chatbot_styles.css              # Chatbot-specific styles
├── .env                            # Environment variables (not committed)
└── README.md                       # Project documentation
```

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Built for the AWS Lambda Hackathon.
- Powered by Streamlit, AWS Lambda, and open-source Python libraries.

---

For questions or support, please open an issue on GitHub.