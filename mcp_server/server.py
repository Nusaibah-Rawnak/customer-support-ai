import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastmcp import FastMCP
from sql_tools import (
    get_customer_by_name,
    get_tickets_by_customer_name,
    get_open_tickets,
    get_all_customers,
    run_sql_query,
)
from rag_tools import (
    search_policies,
    list_uploaded_documents,
    ingest_pdf,
)

mcp = FastMCP("customer-support-mcp")


# SQL Tools 

@mcp.tool()
def tool_get_customer_by_name(name: str) -> str:
    """Look up a customer profile by name. Supports partial name matching."""
    return get_customer_by_name(name)


@mcp.tool()
def tool_get_tickets_by_customer_name(name: str) -> str:
    """Get all support tickets for a specific customer by name."""
    return get_tickets_by_customer_name(name)


@mcp.tool()
def tool_get_open_tickets() -> str:
    """Get all currently open or in-progress support tickets across all customers."""
    return get_open_tickets()


@mcp.tool()
def tool_get_all_customers() -> str:
    """Get a summary list of all customers in the system."""
    return get_all_customers()


@mcp.tool()
def tool_run_sql_query(query: str) -> str:
    """Run a custom read-only SQL SELECT query against the customer database."""
    return run_sql_query(query)


# RAG Tools 

@mcp.tool()
def tool_search_policies(query: str) -> str:
    """Search uploaded policy documents for information relevant to a query."""
    return search_policies(query)


@mcp.tool()
def tool_list_uploaded_documents() -> str:
    """List all policy documents currently stored in the knowledge base."""
    return list_uploaded_documents()


@mcp.tool()
def tool_ingest_pdf(file_path: str) -> str:
    """Ingest a PDF document into the policy knowledge base."""
    return ingest_pdf(file_path)


if __name__ == "__main__":
    mcp.run()