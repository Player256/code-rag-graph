from typing import TypedDict, Annotated, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

from ..model import Model
from .ingestion import run_ingestion_agent
from .query import run_query_agent


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    next: Literal["ingestion", "query", "end"]


class Orchestrator:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("supervisor", self.run_supervisor)
        graph.add_node("ingestion", run_ingestion_agent)
        graph.add_node("query", run_query_agent)

        graph.add_edge(START, "supervisor")
        graph.add_conditional_edges(
            "supervisor",
            self.route_to_agent,
            {"ingestion": "ingestion", "query": "query", "end": END},
        )
        graph.add_edge("ingestion", END)
        graph.add_edge("query", END)

        return graph.compile()

    def run_supervisor(self, state: AgentState) -> AgentState:
        last_message = state["messages"][-1] if state["messages"] else None

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                You are a supervisor agent. Your job is to determine which specialist agent should handle the user's request.
                If the user provides a Git repository URL or asks to 'index' or 'add' a repository, route to the 'ingestion' agent.
                For any other question about a codebase, route to the 'query' agent.
                If the user says 'thanks' or 'done', route to 'end'.
                Respond with 'ingestion', 'query', or 'end' ONLY.
             """,
                ),
                ("user", "{input}"),
            ]
        )

        llm = Model().llm

        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"input": last_message.content if last_message else ""})

        return {
            "next" : response.strip(),
        }

    def route_to_agent(self,state: AgentState) -> Literal["ingestion","query","end"]:
        return state["next"]

    def invoke(self,messages: list[BaseMessage]):
        return self.graph.invoke({"messages":messages})
