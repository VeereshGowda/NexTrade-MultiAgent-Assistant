"""
Tools for the multi-agent supervisor system.
"""

from langchain_core.tools import tool
from langchain_community.document_loaders import WikipediaLoader
from langchain_tavily import TavilySearch
from typing import List, Dict
import requests
import yfinance as yf
from pprint import pformat
from datetime import datetime
from langchain_core.runnables import RunnableConfig
from langgraph.store.memory import InMemoryStore
from langgraph.types import interrupt
from langchain_core.messages import AIMessage, ToolMessage
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

# Global store for memory
_GLOBAL_STORE = None

def initialize_store(store):
    """Initialize the global store."""
    global _GLOBAL_STORE
    _GLOBAL_STORE = store

def get_global_store():
    """Get the global store instance."""
    return _GLOBAL_STORE

# Initialize with InMemoryStore
initialize_store(InMemoryStore())

# Forbidden keywords for web search filtering
FORBIDDEN_KEYWORDS = {
    "403 forbidden", "access denied", "captcha",
    "has been denied", "not authorized", "verify you are a human"
}

@tool
def web_search(query: str, max_results: int = 5) -> Dict[str, List[Dict[str, str]]]:
    """
    General-purpose web search using Tavily API.

    Use when you need recent or broader information from the web to answer the user's request
    (e.g., discover relevant entities, find supporting context, or gather up-to-date references).

    Parameters:
    - query (str): The search query in plain language.
    - max_results (int): Number of results to return (default 5, max 10).

    Returns:
    - {"results": [{"title": str, "url": str, "snippet": str}, ...]}

    Example:
    - query: "emerging AI hardware companies"
    """
    max_results = max(1, min(max_results, 10))
    
    try:
        tavily = TavilySearch(max_results=max_results)
        raw = tavily.invoke({"query": query})

        results = [
            {k: v for k, v in page.items() if k != "raw_content"}  # drop heavy field
            for page in raw["results"]
            if not any(
                k in ((page.get("content") or "").lower())
                for k in FORBIDDEN_KEYWORDS
            )
        ]

        return {"results": results}
    
    except Exception as e:
        return {"results": [], "error": f"Error performing web search: {str(e)}"}


@tool
def wiki_search(topic: str, max_results: int = 5) -> dict:
    """
    Fetch a concise encyclopedic summary for a single entity or topic.

    When to use:
      - You need neutral background about a company, product, person, or concept.

    How to format `topic` (VERY IMPORTANT):
      - Pass a short, Wikipedia-friendly title or entity name.
      - Avoid questions or long queries. Prefer canonical forms.
      - If you have noisy text, reduce it to the key noun phrase.

    Good examples:
      - "NVIDIA", "OpenAI", "Large language model", "Electric vehicle"
    Avoid:
      - "What is NVIDIA and why is it important?", "tell me about AI chips 2025"

    Parameters:
      - topic (str): Canonical page title or concise entity/topic.
    """
    max_results = max(1, min(max_results, 10))
    wiki = WikipediaLoader(query=topic, load_max_docs=max_results)
    raw = wiki.load()

    results = [
      {
        "title": doc.metadata["title"],
        "summary": doc.metadata["summary"],
        "source": doc.metadata["source"]
      }
      for doc in raw
    ]

    return {"results": results}


@tool("lookup_stock")
def lookup_stock_symbol(company_name: str) -> str:
    """
    Converts a company name to its stock symbol using a financial API.

    Parameters:
        company_name (str): The full company name (e.g., 'Tesla').

    Returns:
        str: The stock symbol (e.g., 'TSLA') or an error message.
    """
    # Try simple mapping first for common companies
    try:
        # Common company mappings
        company_mappings = {
            "tesla": "TSLA",
            "apple": "AAPL", 
            "microsoft": "MSFT",
            "microsoft corporation": "MSFT",
            "nvidia": "NVDA",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "meta": "META",
            "facebook": "META",
            "netflix": "NFLX",
            "openai": "MSFT",  # OpenAI is closely tied to Microsoft
            "anthropic": "GOOGL",  # Anthropic has Google investment
        }
        
        company_lower = company_name.lower()
        for key, symbol in company_mappings.items():
            if key in company_lower:
                return symbol
        
        # If no mapping found, try AlphaVantage API
        return _lookup_symbol_api(company_name)
        
    except Exception as e:
        return f"Error looking up symbol for {company_name}: {str(e)}"


def _lookup_symbol_api(company_name: str) -> str:
    """Helper function to lookup symbol using AlphaVantage API."""
    # Use AlphaVantage API for stock symbol lookup
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return f"Symbol lookup for {company_name} requires additional research."
    
    api_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": api_key
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "bestMatches" in data and data["bestMatches"]:
            return data["bestMatches"][0]["1. symbol"]
        else:
            return f"Symbol not found for {company_name}."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to AlphaVantage API: {str(e)}"
    except Exception as e:
        return f"Error looking up symbol for {company_name}: {str(e)}"

@tool("fetch_stock_data")
def fetch_stock_data_raw(stock_symbol: str) -> dict:
    """
    Fetches comprehensive stock data for a given symbol and returns it as a combined dictionary.

    Parameters:
        stock_symbol (str): The stock ticker symbol (e.g., 'TSLA').

    Returns:
        dict: A dictionary combining general stock info and historical market data.
    """
    period = "1mo"
    try:
        stock = yf.Ticker(stock_symbol)

        # Retrieve general stock info and historical market data
        stock_info = stock.info  # Basic company and stock data
        stock_history = stock.history(period=period).to_dict()  # Historical OHLCV data

        # Combine both into a single dictionary
        combined_data = {
            "stock_symbol": stock_symbol,
            "info": stock_info,
            "history": stock_history
        }

        return pformat(combined_data)

    except Exception as e:
        return {"error": f"Error fetching stock data for {stock_symbol}: {str(e)}"}


@tool("place_order")
def place_order(
    symbol: str,
    action: str,
    shares: int,
    limit_price: float,
    order_type: str = "limit"
) -> dict:
    """
    Execute a stock order (simulated) and store it in both memory and database.

    Parameters:
    - symbol: Ticker
    - action: "buy" or "sell"
    - shares: Number of shares to trade (pre-computed by the agent)
    - limit_price: Limit price per share
    - order_type: Order type, default "limit"

    Returns:
    - status: Execution result (simulated)
    - symbol
    - shares
    - limit_price
    - total_spent
    - type: Order type used
    - action
    - storage_results: Results from storage operations
    """
    total_spent = round(int(shares) * limit_price, 2)
    
    storage_results = {
        "memory_stored": False,
        "database_stored": False,
        "errors": []
    }
    
    # Try to store in database (using insert_order)
    try:
        from .database_tools import insert_order
        
        # Try to get the actual user_id from context if available
        # This is a fallback approach for when config isn't directly available
        user_id = "streamlit_user"  # Default fallback
        
        # Create a minimal config
        mock_config = {
            "configurable": {
                "user_id": user_id
            }
        }
        
        # Call the database tool function directly
        database_result = insert_order.func(
            symbol=symbol,
            action=action,
            shares=shares,
            price=limit_price,
            order_type=order_type,
            config=mock_config
        )
        
        if database_result and "error" not in database_result:
            from .database_tools import update_order_status
            update_order_status.func(
                order_id=database_result["order_id"],
                status="filled",
                execution_price=limit_price,
                config=mock_config
            )
            storage_results["database_stored"] = True
            storage_results["order_id"] = database_result["order_id"]
            storage_results["database_id"] = database_result["database_id"]
            print(f"✅ Order stored in database with ID: {database_result['order_id']} for user: {user_id}")
        else:
            storage_results["errors"].append(f"Database error: {database_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        storage_results["errors"].append(f"Database storage error: {e}")
        print(f"⚠️ Failed to store order in database: {e}")
    
    result = {
        "status": "filled",
        "symbol": symbol,
        "shares": int(shares),
        "limit_price": limit_price,
        "total_spent": total_spent,
        "type": order_type,
        "action": action,
        "storage_results": storage_results
    }
    
    print(f"💰 Order executed: {action.upper()} {shares} shares of {symbol} at ${limit_price} (Total: ${total_spent})")
    
    return result

RISKY_TOOLS = {"place_order"}

def halt_on_risky_tools(state):
    """
    Human-in-the-loop safety mechanism for risky trading operations.
    
    This function intercepts calls to risky tools (like place_order) and
    requires human approval before execution.
    
    Args:
        state: The current graph state containing messages
        
    Returns:
        dict: Either empty dict to continue or updated state with cancellation message
    """
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        for tc in last.tool_calls:
            if tc.get("name") in RISKY_TOOLS:
                # Extract order details for approval prompt
                args = tc.get("args", {})
                symbol = args.get("symbol", "Unknown")
                action = args.get("action", "Unknown")
                shares = args.get("shares", 0)
                limit_price = args.get("limit_price", 0)
                total_cost = shares * limit_price if shares and limit_price else 0
                
                # Create detailed approval message
                approval_details = {
                    "tool_name": tc["name"],
                    "symbol": symbol,
                    "action": action.upper(),
                    "shares": shares,
                    "limit_price": limit_price,
                    "total_cost": round(total_cost, 2),
                    "order_details": f"{action.upper()} {shares} shares of {symbol} at ${limit_price} per share (Total: ${round(total_cost, 2)})"
                }
                
                print(f"\n🚨 HUMAN APPROVAL REQUIRED 🚨")
                print(f"Trading Action: {approval_details['order_details']}")
                print(f"Tool: {tc['name']}")
                
                # Request human approval through interrupt
                decision = interrupt({
                    "awaiting": tc["name"], 
                    "args": args,
                    "approval_details": approval_details,
                    "message": f"Do you approve this trading action: {approval_details['order_details']}?"
                })

                # Process the approval decision
                if isinstance(decision, dict) and decision.get("approved", False):
                    print(f"✅ Order approved by human: {approval_details['order_details']}")
                    return {}  # Continue with tool execution

                # If not approved or decision is unclear, cancel the operation
                print(f"❌ Order rejected by human: {approval_details['order_details']}")
                tool_msg = ToolMessage(
                    content=f"🛑 Order cancelled by human approval process.\n\nProposed order: {approval_details['order_details']}\n\nReason: Human intervention required for trading operations. Please provide alternative recommendations or wait for further instructions.",
                    tool_call_id=tc["id"],
                    name=tc["name"]
                )
                return {"messages": [tool_msg]}

    return {}

@tool
def current_timestamp() -> dict:
    """
    Return the current local timestamp.

    Returns:
    - {"iso": str, "epoch": int, "tz": str}
      where:
      - iso: ISO 8601 string with timezone offset
      - epoch: Unix epoch seconds
      - tz: timezone name/offset
    """
    now = datetime.now().astimezone()
    return {
        "iso": now.isoformat(),
        "epoch": int(now.timestamp()),
        "tz": str(now.tzinfo),
    }


@tool
def get_order_history(config: RunnableConfig) -> list:
    """
    Retrieves past investment orders for the current user.
    
    Returns:
        A list of past orders with details including order_id, timestamp, symbol, shares, and price
        
    Example Usage: 
        Review previous investments before recommending new ones
    """
    user_id = config["configurable"].get("user_id")
    namespace = ("ledger", user_id)
    store = get_global_store()
    items = store.search(namespace)
    return [item.value for item in items]
    

@tool
def add_order_to_history(symbol: str, shares: int, price: float, config: RunnableConfig) -> dict:
    """
    Records a new investment order in the user's order history.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        shares: Number of shares purchased or sold (positive for buy, negative for sell)
        price: Price per share in USD
        
    Returns:
        Dictionary containing the newly created order details including order_id and timestamp
        
    Example:
        To record a purchase of 10 shares of Apple at $190.50:
        add_order_to_history(symbol='AAPL', shares=10, price=190.50)
    """
    user_id = config["configurable"].get("user_id")
    namespace = ("ledger", user_id)
    store = get_global_store()

    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "ts": datetime.now().isoformat(),
        "symbol": symbol,
        "shares": shares,
        "price": price
    }
    store.put(namespace, order_id, order)

    return order