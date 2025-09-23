"""
Multi-agent supervisor graph implementation using LangGraph.

This module provides both high-level API and custom implementation approaches
for creating a financial advisor multi-agent system.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph_supervisor import create_supervisor

from .prompts import (
    RESEARCH_SYSTEM_MESSAGE,
    PORTFOLIO_SYSTEM_MESSAGE, 
    SUPERVISOR_SYSTEM_MESSAGE,
    DATABASE_AGENT_SYSTEM_MESSAGE
)
from .tools import (
    web_search,
    wiki_search,
    lookup_stock_symbol,
    fetch_stock_data_raw,
    place_order,
    add_order_to_history,
    current_timestamp,
    get_order_history,
    get_global_store,
    halt_on_risky_tools
)
from .database_tools import (
    insert_order,
    update_order_status,
    get_order_details,
    get_user_orders,
    get_portfolio_positions,
    get_trade_history
)
from .utils import create_handoff_tool, save_graph_image
from .state import SupervisorState

# Load environment variables
load_dotenv()

# Global flag for model preference
_use_azure_model = True


def get_llm(model_name: str = "gpt-4o", use_azure: bool = None):
    """
    Get LLM instance - Azure OpenAI by default, Groq as fallback.
    
    Args:
        model_name: Name of the model to use
        use_azure: Whether to use Azure OpenAI (True) or Groq (False). If None, uses global setting.
        
    Returns:
        LLM instance
    """
    if use_azure is None:
        use_azure = _use_azure_model
        
    if use_azure:
        # Use Azure OpenAI (matching the notebook configuration)
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        
        if not azure_api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI configuration not found. Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")
        
        return AzureChatOpenAI(
            api_key=azure_api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            deployment_name=deployment_name
        )
    else:
        # Fallback to Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        return ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=api_key
        )


def create_research_agent():
    """Create the research agent."""
    return create_react_agent(
        model=get_llm(),
        tools=[web_search, wiki_search],
        prompt=RESEARCH_SYSTEM_MESSAGE,
        name="research"
    )


def create_portfolio_agent():
    """Create the portfolio agent with human-in-the-loop for trading operations."""
    return create_react_agent(
        model=get_llm(),
        tools=[lookup_stock_symbol, fetch_stock_data_raw, place_order, add_order_to_history],
        prompt=PORTFOLIO_SYSTEM_MESSAGE,
        store=get_global_store(),
        version="v2",
        post_model_hook=halt_on_risky_tools,
        name="portfolio"
    )


def create_database_agent():
    """Create the database agent for order and portfolio data management."""
    return create_react_agent(
        model=get_llm(),
        tools=[
            insert_order,
            update_order_status,
            get_order_details,
            get_user_orders,
            get_portfolio_positions,
            get_trade_history
        ],
        prompt=DATABASE_AGENT_SYSTEM_MESSAGE,
        store=get_global_store(),
        version="v2",
        name="database"
    )


def create_supervisor_highlevel():
    """
    Create supervisor using high-level API.
    
    Returns:
        Compiled LangGraph with supervisor functionality
    """
    research_agent = create_research_agent()
    portfolio_agent = create_portfolio_agent()
    database_agent = create_database_agent()
    
    supervisor = create_supervisor(
        agents=[research_agent, portfolio_agent, database_agent],
        tools=[current_timestamp],  # Removed get_order_history - should go through database agent
        model=get_llm(),
        prompt=SUPERVISOR_SYSTEM_MESSAGE,
        version="v2",
        output_mode="full_history",
        store=get_global_store(),
    ).compile(checkpointer=MemorySaver())
    
    return supervisor


def create_supervisor_custom():
    """
    Create supervisor using custom LangGraph primitives.
    
    Returns:
        Compiled LangGraph with custom supervisor implementation
    """
    # Create agents
    research_agent = create_research_agent()
    portfolio_agent = create_portfolio_agent()
    database_agent = create_database_agent()
    
    # Create handoff tools
    assign_to_portfolio_agent = create_handoff_tool(
        agent_name="portfolio",
        description="Transfer to portfolio agent for stock analysis, trading, and investment operations. Provide clear instructions about the specific task.",
    )
    
    assign_to_research_agent = create_handoff_tool(
        agent_name="research", 
        description="Transfer to research agent for investment research and company recommendations. Provide clear instructions about what to research.",
    )
    
    assign_to_database_agent = create_handoff_tool(
        agent_name="database",
        description="Transfer to database agent for order storage, portfolio tracking, and data management. Provide specific instructions about what data to store or retrieve.",
    )
    
    # Create supervisor agent
    supervisor_agent = create_react_agent(
        model=get_llm(),
        tools=[
            current_timestamp,  # Removed get_order_history - should go through database agent
            assign_to_portfolio_agent,
            assign_to_research_agent,
            assign_to_database_agent
        ],
        prompt=SUPERVISOR_SYSTEM_MESSAGE,
        store=get_global_store(),
        name="supervisor"
    )
    
    # Build the graph
    builder = StateGraph(MessagesState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_agent, destinations=("research", "portfolio", "database", END))
    builder.add_node("research", research_agent)
    builder.add_node("portfolio", portfolio_agent)
    builder.add_node("database", database_agent)
    
    # Add edges
    builder.add_edge(START, "supervisor")
    builder.add_edge("research", "supervisor")
    builder.add_edge("portfolio", "supervisor")
    builder.add_edge("database", "supervisor")
    
    # Compile with checkpointer
    supervisor = builder.compile(checkpointer=MemorySaver())
    
    return supervisor


def create_financial_advisor_system(use_highlevel: bool = True, use_azure: bool = True):
    """
    Create the complete financial advisor multi-agent system.
    
    Args:
        use_highlevel: If True, use high-level API. If False, use custom implementation.
        use_azure: If True, use Azure OpenAI. If False, use Groq.
        
    Returns:
        Compiled supervisor graph
    """
    # Store the model preference globally for all agents
    global _use_azure_model
    _use_azure_model = use_azure
    
    if use_highlevel:
        return create_supervisor_highlevel()
    else:
        return create_supervisor_custom()


def save_all_graph_visualizations():
    """Save visualizations for all components."""
    try:
        # Create research agent and save visualization
        research_agent = create_research_agent()
        save_graph_image(research_agent, "research_agent")
        
        # Create portfolio agent and save visualization
        portfolio_agent = create_portfolio_agent()
        save_graph_image(portfolio_agent, "portfolio_agent")
        
        # Create database agent and save visualization
        database_agent = create_database_agent()
        save_graph_image(database_agent, "database_agent")
        
        # Create both supervisor types and save visualizations
        supervisor_highlevel = create_supervisor_highlevel()
        save_graph_image(supervisor_highlevel, "supervisor_highlevel")
        
        supervisor_custom = create_supervisor_custom()
        save_graph_image(supervisor_custom, "supervisor_custom")
        
        print("All graph visualizations saved to 'images/' directory")
        return True
    except Exception as e:
        print(f"Error saving visualizations: {e}")
        return False


# Default export
def get_supervisor():
    """Get the default supervisor instance."""
    return create_financial_advisor_system(use_highlevel=False)


if __name__ == "__main__":
    # For testing purposes, create and save all visualizations
    save_all_graph_visualizations()