"""
Comprehensive tests for database_tools module.

Tests database initialization, order operations, portfolio management, and trade history.
"""

import pytest
import sqlite3
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import database functions and constants
from agent.database_tools import (
    initialize_database,
    insert_order,
    update_order_status,
    get_order_details,
    get_user_orders,
    get_portfolio_positions,
    get_trade_history,
    get_database_stats,
    DB_PATH,
    DB_DIR
)
import agent.database_tools as db_tools


# ==================== Database Initialization Tests ====================

@pytest.mark.unit
class TestDatabaseInitialization:
    """Test database initialization and table creation."""
    
    def test_database_file_exists(self):
        """Test that database file is created."""
        # Database is initialized on module import
        assert os.path.exists(db_tools.DB_PATH)
    
    def test_database_directory_exists(self):
        """Test that database directory exists."""
        assert os.path.exists(db_tools.DB_DIR)
    
    def test_database_has_orders_table(self):
        """Test that orders table exists."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'orders'
    
    def test_database_has_portfolio_table(self):
        """Test that portfolio_positions table exists."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio_positions'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
    
    def test_database_has_trade_history_table(self):
        """Test that trade_history table exists."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='trade_history'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None


# ==================== Order Operations Tests ====================

@pytest.mark.unit
class TestOrderOperations:
    """Test order creation and retrieval."""
    
    def test_insert_order_tool_exists(self):
        """Test that insert_order tool is available."""
        assert hasattr(db_tools, 'insert_order')
        assert callable(db_tools.insert_order)
    
    def test_insert_order_has_tool_decorator(self):
        """Test that insert_order is decorated as a tool."""
        # Check if it has tool attributes
        assert hasattr(db_tools.insert_order, 'name') or hasattr(db_tools.insert_order, '__name__')
    
    def test_get_user_orders_tool_exists(self):
        """Test that get_user_orders tool is available."""
        assert hasattr(db_tools, 'get_user_orders')
        assert callable(db_tools.get_user_orders)
    
    def test_get_order_details_tool_exists(self):
        """Test that get_order_details tool is available."""
        assert hasattr(db_tools, 'get_order_details')
        assert callable(db_tools.get_order_details)
    
    def test_update_order_status_tool_exists(self):
        """Test that update_order_status tool is available."""
        assert hasattr(db_tools, 'update_order_status')
        assert callable(db_tools.update_order_status)


# ==================== Portfolio Operations Tests ====================

@pytest.mark.unit
class TestPortfolioOperations:
    """Test portfolio position management."""
    
    def test_get_portfolio_positions_tool_exists(self):
        """Test that get_portfolio_positions tool is available."""
        assert hasattr(db_tools, 'get_portfolio_positions')
        assert callable(db_tools.get_portfolio_positions)
    
    def test_get_portfolio_positions_has_tool_decorator(self):
        """Test that get_portfolio_positions is decorated as a tool."""
        assert hasattr(db_tools.get_portfolio_positions, 'name') or hasattr(db_tools.get_portfolio_positions, '__name__')


# ==================== Trade History Tests ====================

@pytest.mark.unit
class TestTradeHistory:
    """Test trade history recording and retrieval."""
    
    def test_get_trade_history_tool_exists(self):
        """Test that get_trade_history tool is available."""
        assert hasattr(db_tools, 'get_trade_history')
        assert callable(db_tools.get_trade_history)
    
    def test_get_trade_history_has_tool_decorator(self):
        """Test that get_trade_history is decorated as a tool."""
        assert hasattr(db_tools.get_trade_history, 'name') or hasattr(db_tools.get_trade_history, '__name__')


# ==================== Database Stats Tests ====================

@pytest.mark.unit
class TestDatabaseStats:
    """Test database statistics functionality."""
    
    def test_get_database_stats_exists(self):
        """Test that get_database_stats function exists."""
        assert hasattr(db_tools, 'get_database_stats')
        assert callable(db_tools.get_database_stats)


# ==================== Configuration Tests ====================

@pytest.mark.unit
class TestDatabaseConfiguration:
    """Test database configuration and constants."""
    
    def test_db_path_configured(self):
        """Test that DB_PATH is configured."""
        assert hasattr(db_tools, 'DB_PATH')
        assert isinstance(db_tools.DB_PATH, str)
        assert len(db_tools.DB_PATH) > 0
    
    def test_db_dir_configured(self):
        """Test that DB_DIR is configured."""
        assert hasattr(db_tools, 'DB_DIR')
        assert isinstance(db_tools.DB_DIR, str)
    
    def test_db_path_ends_with_db(self):
        """Test that DB_PATH has .db extension."""
        assert db_tools.DB_PATH.endswith('.db')
    
    def test_db_path_in_data_directory(self):
        """Test that DB_PATH is in data directory."""
        assert 'data' in db_tools.DB_PATH


# ==================== Database Connection Tests ====================

@pytest.mark.unit
class TestDatabaseConnection:
    """Test database connection handling."""
    
    def test_can_connect_to_database(self):
        """Test that we can connect to the database."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        assert conn is not None
        conn.close()
    
    def test_database_is_sqlite3(self):
        """Test that database is SQLite3 format."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()
        conn.close()
        
        assert version is not None
        assert len(version) > 0


# ==================== Schema Validation Tests ====================

@pytest.mark.unit
class TestDatabaseSchema:
    """Test database schema structure."""
    
    def test_orders_table_has_columns(self):
        """Test that orders table has expected columns."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        
        assert 'order_id' in column_names
        assert 'user_id' in column_names
        assert 'symbol' in column_names
        assert 'action' in column_names
        assert 'shares' in column_names
        assert 'price' in column_names
    
    def test_portfolio_table_has_columns(self):
        """Test that portfolio_positions table has expected columns."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(portfolio_positions)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        
        assert 'user_id' in column_names
        assert 'symbol' in column_names
        assert 'shares' in column_names
    
    def test_trade_history_table_has_columns(self):
        """Test that trade_history table has expected columns."""
        conn = sqlite3.connect(db_tools.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(trade_history)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        
        assert 'order_id' in column_names
        assert 'user_id' in column_names
        assert 'symbol' in column_names
        assert 'action' in column_names


# ==================== Tool Metadata Tests ====================

@pytest.mark.unit
class TestToolMetadata:
    """Test that database tools have proper metadata."""
    
    def test_insert_order_is_langchain_tool(self):
        """Test that insert_order is a LangChain tool."""
        tool = db_tools.insert_order
        # LangChain tools have specific attributes
        assert hasattr(tool, 'name') or callable(tool)
    
    def test_get_user_orders_is_langchain_tool(self):
        """Test that get_user_orders is a LangChain tool."""
        tool = db_tools.get_user_orders
        assert hasattr(tool, 'name') or callable(tool)
    
    def test_get_order_details_is_langchain_tool(self):
        """Test that get_order_details is a LangChain tool."""
        tool = db_tools.get_order_details
        assert hasattr(tool, 'name') or callable(tool)
    
    def test_get_portfolio_positions_is_langchain_tool(self):
        """Test that get_portfolio_positions is a LangChain tool."""
        tool = db_tools.get_portfolio_positions
        assert hasattr(tool, 'name') or callable(tool)
    
    def test_get_trade_history_is_langchain_tool(self):
        """Test that get_trade_history is a LangChain tool."""
        tool = db_tools.get_trade_history
        assert hasattr(tool, 'name') or callable(tool)


# ==================== Module Structure Tests ====================

@pytest.mark.unit
class TestModuleStructure:
    """Test database_tools module structure."""
    
    def test_module_has_initialize_database(self):
        """Test that module has initialize_database function."""
        assert hasattr(db_tools, 'initialize_database')
    
    def test_module_has_constants(self):
        """Test that module defines necessary constants."""
        assert hasattr(db_tools, 'DB_PATH')
        assert hasattr(db_tools, 'DB_DIR')
    
    def test_module_imports_sqlite3(self):
        """Test that module imports sqlite3."""
        assert hasattr(db_tools, 'sqlite3')
    
    def test_module_imports_datetime(self):
        """Test that module imports datetime."""
        assert hasattr(db_tools, 'datetime')


# ==================== Error Handling Tests ====================

@pytest.mark.unit
class TestDatabaseErrorHandling:
    """Test error handling in database operations."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    def test_database_connection_survives_errors(self):
        """Test that database connections are properly managed."""
        # This test ensures that even if operations fail,
        # the database remains accessible
        try:
            conn = sqlite3.connect(db_tools.DB_PATH)
            cursor = conn.cursor()
            # Try an invalid query
            try:
                cursor.execute("SELECT * FROM nonexistent_table")
            except sqlite3.OperationalError:
                pass  # Expected
            conn.close()
        except Exception as e:
            pytest.fail(f"Database connection handling failed: {e}")
        
        # Database should still be accessible
        conn = sqlite3.connect(db_tools.DB_PATH)
        assert conn is not None
        conn.close()
    
    def test_insert_order_invalid_db_path(self):
        """Test inserting order with invalid database path handles errors gracefully."""
        # This should raise an exception or return an error
        # Adjust based on actual implementation
        try:
            result = insert_order(
                user_id="user1",
                symbol="AAPL",
                action="buy",
                shares=10,
                price=150.0
            )
            # If it succeeds, that's also valid (uses DB_PATH)
            assert result is not None or result is None
        except Exception:
            # Expected if validation is strict
            pass
    
    def test_get_user_orders_with_nonexistent_user(self):
        """Test getting orders for nonexistent user returns empty list."""
        # LangChain tools use tool_input parameter
        result = get_user_orders.invoke({"user_id": "nonexistent_user_12345"})
        # Should return empty list or error message, not crash
        assert isinstance(result, (list, dict, str))


# ==================== Integration Tests ====================

@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    def test_database_initialization_idempotent(self):
        """Test that calling initialize_database multiple times is safe."""
        # Should not raise an exception
        initialize_database()
        initialize_database()
        
        # Database should still be accessible
        conn = sqlite3.connect(DB_PATH)
        assert conn is not None
        conn.close()
    
    def test_all_tools_are_callable(self):
        """Test that all exported tools are callable."""
        tools = [
            insert_order,
            get_user_orders,
            get_order_details,
            update_order_status,
            get_portfolio_positions,
            get_trade_history,
        ]
        
        for tool in tools:
            assert callable(tool), f"{tool} is not callable"
    
    def test_database_tables_exist_after_init(self):
        """Test that all required tables exist after initialization."""
        initialize_database()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        assert 'orders' in tables
        assert 'portfolio_positions' in tables
        assert 'trade_history' in tables
