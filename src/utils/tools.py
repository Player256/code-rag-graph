import os
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

from ..graph_db.connections import GraphDBConnection
from ..graph_db.ingestion import CodebaseIngestor

NEO4J_SCHEMA = """
Node Labels and Properties:
- File: {path: string}
- Module: {name: string}
- Class: {name: string, file_path: string}
- Function: {name: string, file_path: string, docstring: string}

Relationship Types:
- IMPORTS: (File)-[:IMPORTS]->(Module)
- DEFINES_CLASS: (File)-[:DEFINES_CLASS]->(Class)
- DEFINES_FUNCTION: (File or Class)-[:DEFINES_FUNCTION]->(Function)
- CALLS: (Function)-[:CALLS]->(Function)
- INHERITS_FROM: (Class)-[:INHERITS_FROM]->(Class)
"""


@tool
def index_repository(repo_url: str) -> str:
    """
    Clones a Git repository from a given URL, parses its Python files,
    and ingests the code structure into the Neo4j knowledge graph.
    This tool should be used to add a new codebase to the system for analysis.
    """
    try:
        local_path = os.path.join("/tmp/code_navigator_repos", repo_url.split("/")[-1])
        ingestor = CodebaseIngestor()
        ingestor.ingest_repository(repo_url, local_path)
        return f"Successfully indexed the repository: {repo_url}"
    except Exception as e:
        return f"Failed to index repository {repo_url}. Error: {e}"


@tool
def generate_cypher_query(question: str) -> str:
    """
    Takes a user's natural language question about a codebase and converts it
    into a Cypher query for execution against the Neo4j graph database.
    Use this tool to formulate a database query before executing it.
    The database schema is as follows:
    {schema}
    """
    cypher_generation_template = f"""
    You are an expert Neo4j developer. Your task is to write Cypher queries
    to answer questions about a software codebase.

    Database Schema:
    {NEO4J_SCHEMA}

    Question:
    {{question}}

    Cypher Query:
    """

    prompt = ChatPromptTemplate.from_template(cypher_generation_template)
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"question": question, "schema": NEO4J_SCHEMA})


@tool
def execute_cypher_query(query: str) -> list[dict]:
    """
    Executes a given Cypher query against the Neo4j graph database and returns
    the results as a list of dictionaries. This tool should be used after
    a Cypher query has been generated to retrieve data from the graph.
    """
    driver = GraphDBConnection.get_driver()
    try:
        with driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
    except Exception as e:
        return [{"error": f"Query failed to execute. Error: {e}"}]
