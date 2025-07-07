# Code Navigator CLI

Code Navigator is a command-line tool designed to help developers understand complex codebases. It works by indexing a Git repository into a Neo4j graph database and allowing you to ask natural language questions about the code. The tool uses Large Language Models (LLMs) to parse your questions, generate database queries, and provide answers about the codebase's structure, including files, classes, functions, and their relationships.

## Features

*   **Codebase Indexing**: Clones any public Git repository and maps its structure into a graph database.
*   **AST-based Parsing**: Analyzes Python source files to identify key entities like classes, functions, imports, and calls.
*   **Natural Language Queries**: Ask questions like "What does the `run_query_agent` function do?" or "Which classes inherit from `BaseMessage`?".
*   **LLM-Powered Query Generation**: Automatically converts your questions into Cypher queries to be executed against the Neo4j database.
*   **Interactive CLI**: A simple command-line interface for indexing repositories and asking questions.

## Prerequisites

Before you begin, ensure you have the following installed:
*   Python 3.11 or higher
*   Docker and Docker Compose
*   An AWS account with access to Amazon Bedrock, with your AWS credentials configured in your environment.

## Installation and Setup

Follow these steps to get the Code Navigator CLI running on your local machine.

**1. Clone the Repository**
First, clone this repository to your local machine:
```bash
git clone 
cd 
```

**2. Set Up a Python Environment**
It is recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

**3. Install Dependencies(will be updated later)**
Install the required Python packages. You will need to create a `requirements.txt` file with the necessary libraries (e.g., `langchain`, `langchain-aws`, `neo4j`, `prompt-toolkit`, `python-dotenv`, `gitpython`).
```bash
pip install -r requirements.txt
```

**4. Start the Neo4j Database**
The application uses a Neo4j database running in a Docker container. Start the service using Docker Compose:
```bash
docker-compose up -d
```
This command starts the Neo4j container in the background. You can access the Neo4j browser interface at `http://localhost:7474`.

**5. Configure Environment Variables**
The application requires credentials to connect to the Neo4j database. Create a file named `.env` in the root of the project directory.
```bash
touch .env
```
Add the following lines to the `.env` file. These credentials must match the ones specified in the `docker-compose.yml` file.
```env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<password>
```

## How to Use

Once the setup is complete, you can run the application from the root directory of the project.

**1. Start the CLI**
```bash
python main.py
```
You will be greeted with a welcome message and a prompt.

**2. View Available Commands**
Type `help` to see a list of all available commands.
```
> help
```

**3. Index a Repository**
Before you can ask questions, you must index a codebase. Use the `index` command followed by the URL of a public Git repository.
```
> index https://github.com/vllm-project/vllm
```
The tool will clone the repository, parse its Python files, and load the structure into the database.

**4. Ask a Question**
Once a repository is indexed, you can ask questions about it using the `ask` command.
```
> ask How is the model class designed in the vllm repository?
```
The tool will use an LLM to generate and execute a Cypher query to find the answer and return a human-readable response.

**5. Exit the Application**
To close the CLI, type `exit`.
```
> exit
```

## Project Structure

The project is organized into several directories to separate concerns:
```
└── src/
    ├── agents/        # Contains the specialist agents (ingestion, query) and the orchestrator
    ├── cli/           # Handles the command-line interface logic
    ├── graph_db/      # Manages the Neo4j connection, data ingestion, and Cypher queries
    ├── model.py       # Configures and provides the Bedrock LLM
    └── utils/         # Contains utility functions and tool definitions for the agents
```
