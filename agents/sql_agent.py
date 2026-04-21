import os
import sys
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))
from agents.rag_agent import SYSTEM_PROMPT
from sql_tools import (
    get_customer_by_name,
    get_tickets_by_customer_name,
    get_open_tickets,
    get_all_customers,
    run_sql_query,
)


@tool
def lookup_customer(name: str) -> str:
    """Look up a customer profile by name."""
    return get_customer_by_name(name)


@tool
def lookup_tickets(name: str) -> str:
    """Get all support tickets for a customer by name."""
    return get_tickets_by_customer_name(name)


@tool
def open_tickets() -> str:
    """Get all open or in-progress support tickets."""
    return get_open_tickets()


@tool
def all_customers() -> str:
    """Get a list of all customers."""
    return get_all_customers()


@tool
def custom_sql(query: str) -> str:
    """Run a custom SELECT SQL query against the database."""
    return run_sql_query(query)


SQL_TOOLS = [lookup_customer, lookup_tickets, open_tickets, all_customers, custom_sql]

SYSTEM_PROMPT = """You are a helpful customer support assistant with access to a customer database.
You can look up customer profiles, support ticket history, and run queries.

The database has two tables:
- customers: id, name, email, phone, plan, joined_date, country
- support_tickets: id, customer_id, subject, description, status, priority, created_date, resolved_date

The 'plan' column has values: Basic, Premium, Enterprise.
The 'status' column has values: Open, In Progress, Resolved, Closed.

When answering:
- Always be concise and friendly
- Summarize data clearly in plain English
- If asked for an overview, include both profile info and recent tickets
- Format dates in a readable way (e.g. March 15, 2022)
- Group tickets by status when listing multiple
"""


def get_sql_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1,
        disable_streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, SQL_TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=SQL_TOOLS, verbose=False)


def run_sql_agent(query: str) -> str:
    agent = get_sql_agent()
    result = agent.invoke({"input": query})
    output = result["output"]
    # Handle Gemini 2.5's structured output format
    if isinstance(output, list):
        return "".join(item.get("text", "") for item in output if isinstance(item, dict))
    return output


if __name__ == "__main__":
    print(run_sql_agent("Give me an overview of Ema's profile and support tickets."))