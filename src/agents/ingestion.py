from langchain_core.messages import BaseMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from model import Model

from ..utils.tools import index_repository
from langchain_core.prompts import ChatPromptTemplate

def create_ingestion_agent_executor() -> AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system","You are an assistant that indexes code repositories. Use the index_repository tool when user provides a repository URL. "),
            ("user","{input}"),
            ("placeholder","{agent_scratchpad}"),
        ]
    )
    
    llm = Model.get_model()
    tools = [index_repository]
    agent = create_tool_calling_agent(llm,tools,prompt)
    executor = AgentExecutor(agent=agent,tools=tools,verbose=True)
    
    return executor


def run_ingestion_agent(state: dict) -> dict:
    agent = create_ingestion_agent_executor()
    last_message = state["messages"][-1]
    response = agent.invoke({
        "input" : last_message.content,
    })
    
    return {
        "messages" : [response["output"]]
    }
    
