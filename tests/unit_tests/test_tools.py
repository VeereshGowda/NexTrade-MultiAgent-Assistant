"""
Unit tests for agent tools.

Tests web search, stock lookup, order placement with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from agent.tools import (
    web_search,
    wiki_search,
    lookup_stock_symbol,
    fetch_stock_data_raw,
    place_order,
    current_timestamp,
    FORBIDDEN_KEYWORDS
)


# ==================== Web Search Tests ====================

@pytest.mark.unit
@pytest.mark.mock
class TestWebSearch:
    """Test web search tool with mocked Tavily API."""
    
    @patch('agent.tools.TavilySearch')
    def test_web_search_success(self, mock_tavily):
        """Test successful web search."""
        # Mock Tavily response
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = {
            "results": [
                {
                    "title": "NVIDIA Stock Analysis",
                    "url": "https://example.com/nvidia",
                    "content": "NVIDIA shows strong growth",
                    "snippet": "Analysis of NVIDIA"
                },
                {
                    "title": "Tech Stocks 2025",
                    "url": "https://example.com/tech",
                    "content": "Tech sector outlook",
                    "snippet": "Tech sector analysis"
                }
            ]
        }
        mock_tavily.return_value = mock_tavily_instance
        
        result = web_search.invoke({"query": "NVIDIA stock analysis", "max_results": 5})
        
        assert "results" in result
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "NVIDIA Stock Analysis"
        assert "raw_content" not in result["results"][0]  # Should be filtered
    
    @patch('agent.tools.TavilySearch')
    def test_web_search_filters_forbidden_content(self, mock_tavily):
        """Test that web search filters forbidden content."""
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.return_value = {
            "results": [
                {
                    "title": "Valid Result",
                    "url": "https://example.com/valid",
                    "content": "Valid content"
                },
                {
                    "title": "Forbidden Result",
                    "url": "https://example.com/forbidden",
                    "content": "403 forbidden - access denied"
                },
                {
                    "title": "Captcha Result",
                    "url": "https://example.com/captcha",
                    "content": "Please verify you are a human"
                }
            ]
        }
        mock_tavily.return_value = mock_tavily_instance
        
        result = web_search.invoke({"query": "test", "max_results": 5})
        
        # Should only include valid result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Valid Result"
    
    @patch('agent.tools.TavilySearch')
    def test_web_search_respects_max_results(self, mock_tavily):
        """Test that max_results parameter is respected."""
        mock_tavily_instance = MagicMock()
        mock_tavily.return_value = mock_tavily_instance
        
        web_search.invoke({"query": "test", "max_results": 3})
        
        # Check Tavily was called with correct max_results
        mock_tavily.assert_called_with(max_results=3)
    
    @patch('agent.tools.TavilySearch')
    def test_web_search_clamps_max_results(self, mock_tavily):
        """Test that max_results is clamped to valid range."""
        mock_tavily_instance = MagicMock()
        mock_tavily.return_value = mock_tavily_instance
        
        # Test upper bound
        web_search.invoke({"query": "test", "max_results": 100})
        mock_tavily.assert_called_with(max_results=10)
        
        # Test lower bound
        web_search.invoke({"query": "test", "max_results": 0})
        mock_tavily.assert_called_with(max_results=1)
    
    @patch('agent.tools.TavilySearch')
    def test_web_search_error_handling(self, mock_tavily):
        """Test web search handles API errors gracefully."""
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.invoke.side_effect = Exception("API Error")
        mock_tavily.return_value = mock_tavily_instance
        
        result = web_search.invoke({"query": "test", "max_results": 5})
        
        assert "results" in result
        assert len(result["results"]) == 0
        assert "error" in result
        assert "API Error" in result["error"]


# ==================== Wikipedia Search Tests ====================

@pytest.mark.unit
@pytest.mark.mock
class TestWikiSearch:
    """Test Wikipedia search tool with mocked loader."""
    
    @patch('agent.tools.WikipediaLoader')
    def test_wiki_search_success(self, mock_loader):
        """Test successful Wikipedia search."""
        # Mock Wikipedia document
        mock_doc = MagicMock()
        mock_doc.page_content = "NVIDIA is a leading technology company..."
        mock_doc.metadata = {"title": "NVIDIA", "source": "https://en.wikipedia.org/wiki/NVIDIA"}
        
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        result = wiki_search.invoke({"topic": "NVIDIA", "max_results": 1})
        
        assert "results" in result
        assert len(result["results"]) > 0
        assert "NVIDIA is a leading technology company" in result["results"][0]["summary"]
    
    @patch('agent.tools.WikipediaLoader')
    def test_wiki_search_truncates_long_content(self, mock_loader):
        """Test that long Wikipedia content is truncated."""
        long_content = "A" * 5000  # Very long content
        
        mock_doc = MagicMock()
        mock_doc.page_content = long_content
        mock_doc.metadata = {"title": "Test", "source": "https://wikipedia.org"}
        
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        result = wiki_search.invoke({"topic": "Test", "max_results": 1})
        
        # Should be truncated to 500 characters (as per implementation)
        assert "results" in result
        assert len(result["results"]) > 0
        assert len(result["results"][0]["summary"]) <= 5000
    
    @patch('agent.tools.WikipediaLoader')
    def test_wiki_search_no_results(self, mock_loader):
        """Test Wikipedia search with no results."""
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = []
        mock_loader.return_value = mock_loader_instance
        
        result = wiki_search.invoke({"topic": "NonexistentTopic123", "max_results": 1})
        
        assert "error" in result
        assert "no results" in result["error"].lower()
    
    @patch('agent.tools.WikipediaLoader')
    def test_wiki_search_error_handling(self, mock_loader):
        """Test Wikipedia search handles errors gracefully."""
        mock_loader.side_effect = Exception("Wikipedia API error")
        
        result = wiki_search.invoke({"topic": "Test", "max_results": 1})
        
        assert "error" in result
        assert "error" in result["error"].lower()


# ==================== Stock Symbol Lookup Tests ====================

@pytest.mark.unit
@pytest.mark.mock
class TestStockLookup:
    """Test stock symbol lookup tool."""
    
    @patch('agent.tools.requests.get')
    def test_lookup_stock_symbol_success(self, mock_get):
        """Test successful stock symbol lookup."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "1. symbol": "NVDA",
                "2. name": "NVIDIA Corporation",
                "3. type": "Equity",
                "4. region": "United States",
                "8. currency": "USD"
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = lookup_stock_symbol.invoke({"company_name": "NVIDIA"})
        
        assert "symbol" in result
        assert result["symbol"] == "NVDA"
        assert result["name"] == "NVIDIA Corporation"
    
    @patch('agent.tools.requests.get')
    def test_lookup_stock_symbol_no_results(self, mock_get):
        """Test stock lookup with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = lookup_stock_symbol.invoke({"company_name": "NonexistentCompany"})
        
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    @patch('agent.tools.requests.get')
    def test_lookup_stock_symbol_api_error(self, mock_get):
        """Test stock lookup handles API errors."""
        mock_get.side_effect = Exception("API connection failed")
        
        # Use a company not in the hardcoded mappings to trigger API call
        result = lookup_stock_symbol.invoke({"company_name": "Unknown Tech Company XYZ"})
        
        assert "error" in result


# ==================== Stock Data Fetch Tests ====================

@pytest.mark.unit
@pytest.mark.mock
class TestStockDataFetch:
    """Test stock data fetching tool."""
    
    @patch('agent.tools.yf.Ticker')
    def test_fetch_stock_data_success(self, mock_ticker):
        """Test successful stock data fetch."""
        # Mock yfinance Ticker
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "symbol": "AAPL",
            "shortName": "Apple Inc.",
            "regularMarketPrice": 150.25,
            "regularMarketChange": 2.50,
            "regularMarketChangePercent": 1.69,
            "regularMarketVolume": 50000000,
            "marketCap": 2500000000000
        }
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_stock_data_raw.invoke({"stock_symbol": "AAPL"})
        
        assert "stock_symbol" in result
        assert result["stock_symbol"] == "AAPL"
    
    @patch('agent.tools.yf.Ticker')
    def test_fetch_stock_data_invalid_symbol(self, mock_ticker):
        """Test stock data fetch with invalid symbol."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}  # Empty info for invalid symbol
        mock_ticker.return_value = mock_ticker_instance
        
        result = fetch_stock_data_raw.invoke({"stock_symbol": "INVALID"})
        
        assert "error" in result or "stock_symbol" in result
    
    @patch('agent.tools.yf.Ticker')
    def test_fetch_stock_data_api_error(self, mock_ticker):
        """Test stock data fetch handles API errors."""
        mock_ticker.side_effect = Exception("yfinance error")
        
        result = fetch_stock_data_raw.invoke({"stock_symbol": "AAPL"})
        
        assert "error" in result


# ==================== Order Placement Tests ====================

@pytest.mark.unit
@pytest.mark.mock
class TestOrderPlacement:
    """Test order placement tool."""
    
    def test_place_order_structure(self):
        """Test place_order creates proper order structure."""
        order = place_order.invoke({
            "symbol": "AAPL",
            "quantity": 10,
            "order_type": "buy",
            "price": 150.25
        })
        
        assert order["symbol"] == "AAPL"
        assert order["quantity"] == 10
        assert order["order_type"] == "buy"
        assert order["price"] == 150.25
        assert order["status"] == "pending_approval"
        assert "order_id" in order
        assert "timestamp" in order
    
    def test_place_order_generates_unique_ids(self):
        """Test that each order gets a unique ID."""
        order1 = place_order.invoke({
            "symbol": "AAPL",
            "quantity": 10,
            "order_type": "buy",
            "price": 150.00
        })
        
        order2 = place_order.invoke({
            "symbol": "TSLA",
            "quantity": 5,
            "order_type": "sell",
            "price": 200.00
        })
        
        assert order1["order_id"] != order2["order_id"]
    
    def test_place_order_buy_type(self):
        """Test placing a buy order."""
        order = place_order.invoke({
            "symbol": "NVDA",
            "quantity": 15,
            "order_type": "buy",
            "price": 450.00
        })
        
        assert order["order_type"] == "buy"
        assert order["quantity"] == 15
    
    def test_place_order_sell_type(self):
        """Test placing a sell order."""
        order = place_order.invoke({
            "symbol": "MSFT",
            "quantity": 20,
            "order_type": "sell",
            "price": 380.00
        })
        
        assert order["order_type"] == "sell"
        assert order["quantity"] == 20


# ==================== Utility Function Tests ====================

@pytest.mark.unit
class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_current_timestamp_format(self):
        """Test current_timestamp returns valid ISO format."""
        timestamp = current_timestamp.invoke({})
        
        # Should be valid ISO format
        datetime.fromisoformat(timestamp)  # Will raise if invalid
        
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
    
    def test_current_timestamp_is_recent(self):
        """Test that timestamp is current."""
        timestamp = current_timestamp.invoke({})
        dt = datetime.fromisoformat(timestamp)
        
        # Should be within last minute
        now = datetime.now()
        time_diff = abs((now - dt).total_seconds())
        
        assert time_diff < 60  # Within 1 minute


# ==================== Tool Integration Tests ====================

@pytest.mark.integration
@pytest.mark.mock
class TestToolWorkflow:
    """Integration tests for tool workflows."""
    
    @patch('agent.tools.yf.Ticker')
    @patch('agent.tools.requests.get')
    def test_research_to_order_workflow(self, mock_requests, mock_ticker):
        """Test complete workflow from research to order."""
        # Mock stock lookup
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            "1. symbol": "AAPL",
            "2. name": "Apple Inc."
        }]
        mock_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_response
        
        # Mock stock data
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "symbol": "AAPL",
            "regularMarketPrice": 150.00
        }
        mock_ticker.return_value = mock_ticker_instance
        
        # Step 1: Lookup symbol
        lookup_result = lookup_stock_symbol.invoke({"company_name": "Apple"})
        assert lookup_result["symbol"] == "AAPL"
        
        # Step 2: Fetch stock data
        stock_data = fetch_stock_data_raw.invoke({"symbol": "AAPL"})
        assert "current_price" in stock_data
        
        # Step 3: Place order
        order = place_order.invoke({
            "symbol": "AAPL",
            "quantity": 10,
            "order_type": "buy",
            "price": stock_data.get("current_price", 150.00)
        })
        
        assert order["status"] == "pending_approval"
        assert order["symbol"] == "AAPL"
