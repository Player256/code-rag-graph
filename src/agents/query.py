from langchain_core.messages import BaseMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from ..model import Model
from langchain_core.prompts import ChatPromptTemplate
from ..utils.tools import generate_cypher_query, execute_cypher_query


def create_query_agent_executor() -> AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert software engineer. You answer questions about a codebase by first generating a Cypher query, then executing it to retrieve information from a graph database, and finally synthesizing a human-readable response based on the results.",
            ),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    llm = Model().llm
    tools = [
        generate_cypher_query,
        execute_cypher_query,
    ]
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent,tools=tools,verbose=True)
    return executor

def run_query_agent(state:dict) -> dict:
    agent = create_query_agent_executor()
    last_message = state["messages"][-1]
    response = agent.invoke({
        "input" : last_message.content,
    })
    
    return {
        "messages" : [response["output"]]
    }
