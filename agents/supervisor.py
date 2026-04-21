import os
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# Import specialist agents
import sys
sys.path.insert(0, os.path.dirname(__file__))
from sql_agent import run_sql_agent
from rag_agent import run_rag_agent


# State 

class AgentState(TypedDict):
    query: str
    route: Literal["sql", "rag", "general"]
    response: str


# Nodes 

def classify_query(state: AgentState) -> AgentState:
    """Use LLM to classify the query and decide which agent to route to."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0,
        disable_streaming=True,
    )

    classification_prompt = f"""You are a routing assistant. Classify the following user query into one of these categories:

- "sql": Questions about customer profiles, support tickets, customer history, account details, or any structured customer data
- "rag": Questions about company policies, refund policy, terms of service, procedures, guidelines, or any policy documents
- "general": General greetings, small talk, or questions that don't fit either category

Query: "{state['query']}"

Respond with ONLY one word: sql, rag, or general"""

    result = llm.invoke([HumanMessage(content=classification_prompt)])
    route = result.content.strip().lower()

    if route not in ["sql", "rag", "general"]:
        route = "general"

    return {**state, "route": route}


def route_query(state: AgentState) -> str:
    """Return the next node based on the route."""
    return state["route"]


def sql_node(state: AgentState) -> AgentState:
    """Run the SQL agent."""
    response = run_sql_agent(state["query"])
    return {**state, "response": response}


def rag_node(state: AgentState) -> AgentState:
    """Run the RAG agent."""
    response = run_rag_agent(state["query"])
    return {**state, "response": response}


def general_node(state: AgentState) -> AgentState:
    """Handle general queries directly."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        disable_streaming=True,
    )
    result = llm.invoke([HumanMessage(content=state["query"])])
    return {**state, "response": result.content}


# Graph 

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_query)
    graph.add_node("sql", sql_node)
    graph.add_node("rag", rag_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_query,
        {
            "sql": "sql",
            "rag": "rag",
            "general": "general",
        }
    )

    graph.add_edge("sql", END)
    graph.add_edge("rag", END)
    graph.add_edge("general", END)

    return graph.compile()


def run_supervisor(query: str) -> dict:
    """Run the full multi-agent pipeline and return response + route info."""
    app = build_graph()
    result = app.invoke({
        "query": query,
        "route": "general",
        "response": "",
    })
    return {
        "response": result["response"],
        "route": result["route"],
    }


if __name__ == "__main__":
    # Test all three routes
    tests = [
        "Give me an overview of Ema's profile and support tickets.",
        "What is the refund policy?",
        "Hello, how are you?",
    ]
    for q in tests:
        print(f"\nQ: {q}")
        result = run_supervisor(q)
        print(f"Route: {result['route']}")
        print(f"A: {result['response']}")