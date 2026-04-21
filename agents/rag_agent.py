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
from rag_tools import search_policies, list_uploaded_documents


@tool
def search_policy_docs(query: str) -> str:
    """Search uploaded policy documents for relevant information."""
    return search_policies(query)


@tool
def list_documents() -> str:
    """List all policy documents currently in the knowledge base."""
    return list_uploaded_documents()


RAG_TOOLS = [search_policy_docs, list_documents]

SYSTEM_PROMPT = """You are a helpful customer support assistant with access to company policy documents.
You can search through uploaded PDFs to answer questions about company policies, procedures, and guidelines.

When answering:
- Always base your answers on the retrieved document content
- Be concise and clear
- If the documents don't contain relevant information, say so honestly
- Mention which document the information came from when possible
- If no documents have been uploaded, let the user know they need to upload policy PDFs first
"""


def get_rag_agent():
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

    agent = create_tool_calling_agent(llm, RAG_TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=RAG_TOOLS, verbose=False)


def run_rag_agent(query: str) -> str:
    agent = get_rag_agent()
    result = agent.invoke({"input": query})
    output = result["output"]
    # Handle Gemini 2.5's structured output format
    if isinstance(output, list):
        return "".join(item.get("text", "") for item in output if isinstance(item, dict))
    return output


if __name__ == "__main__":
    print(run_rag_agent("What is the refund policy?"))