"""
Database tools for managing order details in SQLite.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
import uuid


# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'trading_orders.db')
DB_DIR = os.path.dirname(DB_PATH)

def initialize_database():
    """Initialize the SQLite database with required tables."""
    # Create data directory if it doesn't exist
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,  -- 'buy' or 'sell'
            shares INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            order_type TEXT DEFAULT 'limit',  -- 'market', 'limit', 'stop'
            status TEXT DEFAULT 'pending',  -- 'pending', 'filled', 'cancelled', 'rejected'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_price REAL,
            execution_time TIMESTAMP,
            notes TEXT
        )
    ''')
    
    # Create portfolio positions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            shares INTEGER NOT NULL,
            average_price REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, symbol)
        )
    ''')
    
    # Create trade history table for detailed tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            shares INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            commission REAL DEFAULT 0.0,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

# Initialize database on module import
initialize_database()


@tool
def insert_order(
    symbol: str,
    action: str,
    shares: int,
    price: float,
    order_type: str = "limit",
    config: RunnableConfig = None
) -> Dict:
    """
    Insert a new order into the database.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'NVDA')
        action: 'buy' or 'sell'
        shares: Number of shares
        price: Price per share
        order_type: Type of order ('market', 'limit', 'stop')
        config: Configuration containing user_id
        
    Returns:
        Dictionary with order details and database ID
    """
    try:
        # Get user_id from config
        user_id = config["configurable"].get("user_id", "default_user") if config else "default_user"
        
        # Generate unique order ID
        order_id = str(uuid.uuid4())
        
        # Calculate total amount
        total_amount = shares * price
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert order
        cursor.execute('''
            INSERT INTO orders (
                order_id, user_id, symbol, action, shares, price, 
                total_amount, order_type, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id, user_id, symbol.upper(), action.lower(), 
            shares, price, total_amount, order_type.lower(), 'pending'
        ))
        
        # Get the database row ID
        db_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        order_details = {
            "database_id": db_id,
            "order_id": order_id,
            "user_id": user_id,
            "symbol": symbol.upper(),
            "action": action.lower(),
            "shares": shares,
            "price": price,
            "total_amount": total_amount,
            "order_type": order_type.lower(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        print(f"✅ Order inserted: {action.upper()} {shares} shares of {symbol} at ${price}")
        return order_details
        
    except Exception as e:
        error_msg = f"❌ Failed to insert order: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


@tool
def update_order_status(
    order_id: str,
    status: str,
    execution_price: Optional[float] = None,
    notes: Optional[str] = None,
    config: RunnableConfig = None
) -> Dict:
    """
    Update the status of an existing order.
    
    Args:
        order_id: Unique order identifier
        status: New status ('filled', 'cancelled', 'rejected')
        execution_price: Actual execution price (if filled)
        notes: Additional notes about the order
        config: Configuration containing user_id
        
    Returns:
        Dictionary with update confirmation
    """
    try:
        user_id = config["configurable"].get("user_id", "default_user") if config else "default_user"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build update query
        update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status.lower()]
        
        if execution_price is not None:
            update_fields.append("execution_price = ?")
            update_fields.append("execution_time = CURRENT_TIMESTAMP")
            params.append(execution_price)
        
        if notes:
            update_fields.append("notes = ?")
            params.append(notes)
        
        # Add WHERE conditions
        params.extend([order_id, user_id])
        
        query = f'''
            UPDATE orders 
            SET {", ".join(update_fields)}
            WHERE order_id = ? AND user_id = ?
        '''
        
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            conn.close()
            return {"error": f"Order {order_id} not found for user {user_id}"}
        
        # If order is filled, add to trade history
        if status.lower() == 'filled':
            # Get order details
            cursor.execute('''
                SELECT symbol, action, shares, price, total_amount 
                FROM orders WHERE order_id = ?
            ''', (order_id,))
            
            order_data = cursor.fetchone()
            if order_data:
                symbol, action, shares, price, total_amount = order_data
                
                # Add to trade history
                cursor.execute('''
                    INSERT INTO trade_history (
                        order_id, user_id, symbol, action, shares, price, total_amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (order_id, user_id, symbol, action, shares, execution_price or price, total_amount))
                
                # Update portfolio positions
                if action == 'buy':
                    # Add to portfolio
                    cursor.execute('''
                        INSERT OR REPLACE INTO portfolio_positions (user_id, symbol, shares, average_price, last_updated)
                        VALUES (?, ?, 
                            COALESCE((SELECT shares FROM portfolio_positions WHERE user_id = ? AND symbol = ?), 0) + ?,
                            (COALESCE((SELECT shares * average_price FROM portfolio_positions WHERE user_id = ? AND symbol = ?), 0) + ?) / 
                            (COALESCE((SELECT shares FROM portfolio_positions WHERE user_id = ? AND symbol = ?), 0) + ?),
                            CURRENT_TIMESTAMP)
                    ''', (user_id, symbol, user_id, symbol, shares, 
                          user_id, symbol, total_amount, 
                          user_id, symbol, shares))
                elif action == 'sell':
                    # Remove from portfolio
                    cursor.execute('''
                        UPDATE portfolio_positions 
                        SET shares = shares - ?, last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND symbol = ?
                    ''', (shares, user_id, symbol))
                    
                    # Remove position if shares become 0 or negative
                    cursor.execute('''
                        DELETE FROM portfolio_positions 
                        WHERE user_id = ? AND symbol = ? AND shares <= 0
                    ''', (user_id, symbol))
        
        conn.commit()
        conn.close()
        
        result = {
            "order_id": order_id,
            "status": status.lower(),
            "updated_at": datetime.now().isoformat(),
            "message": f"Order {order_id} status updated to {status.lower()}"
        }
        
        if execution_price:
            result["execution_price"] = execution_price
            
        print(f"✅ Order {order_id} status updated to {status.lower()}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Failed to update order: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


@tool
def get_order_details(order_id: str, config: RunnableConfig = None) -> Dict:
    """
    Retrieve details for a specific order.
    
    Args:
        order_id: Unique order identifier
        config: Configuration containing user_id
        
    Returns:
        Dictionary with order details
    """
    try:
        user_id = config["configurable"].get("user_id", "default_user") if config else "default_user"
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM orders 
            WHERE order_id = ? AND user_id = ?
        ''', (order_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"error": f"Order {order_id} not found for user {user_id}"}
        
        # Convert row to dictionary
        order_details = dict(row)
        
        print(f"✅ Retrieved order details for {order_id}")
        return order_details
        
    except Exception as e:
        error_msg = f"❌ Failed to retrieve order: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


@tool
def get_user_orders(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    config: RunnableConfig = None
) -> Dict:
    """
    Retrieve orders for a user with optional filtering.
    
    Args:
        user_id: User identifier (uses config if not provided)
        status: Filter by order status
        symbol: Filter by stock symbol
        limit: Maximum number of orders to return
        config: Configuration containing user_id
        
    Returns:
        Dictionary with list of orders
    """
    try:
        if not user_id and config:
            user_id = config["configurable"].get("user_id", "default_user")
        elif not user_id:
            user_id = "default_user"
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = ["user_id = ?"]
        params = [user_id]
        
        if status:
            where_conditions.append("status = ?")
            params.append(status.lower())
        
        if symbol:
            where_conditions.append("symbol = ?")
            params.append(symbol.upper())
        
        query = f'''
            SELECT * FROM orders 
            WHERE {" AND ".join(where_conditions)}
            ORDER BY created_at DESC 
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dictionaries
        orders = [dict(row) for row in rows]
        
        result = {
            "user_id": user_id,
            "total_orders": len(orders),
            "orders": orders
        }
        
        if status:
            result["filtered_by_status"] = status
        if symbol:
            result["filtered_by_symbol"] = symbol
        
        print(f"✅ Retrieved {len(orders)} orders for user {user_id}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Failed to retrieve orders: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


@tool
def get_portfolio_positions(user_id: Optional[str] = None, config: RunnableConfig = None) -> Dict:
    """
    Retrieve current portfolio positions for a user.
    
    Args:
        user_id: User identifier (uses config if not provided)
        config: Configuration containing user_id
        
    Returns:
        Dictionary with portfolio positions
    """
    try:
        if not user_id and config:
            user_id = config["configurable"].get("user_id", "default_user")
        elif not user_id:
            user_id = "default_user"
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, shares, average_price, 
                   (shares * average_price) as total_value,
                   last_updated
            FROM portfolio_positions 
            WHERE user_id = ? AND shares > 0
            ORDER BY symbol
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        positions = [dict(row) for row in rows]
        
        # Calculate total portfolio value
        total_value = sum(pos['total_value'] for pos in positions)
        
        result = {
            "user_id": user_id,
            "total_positions": len(positions),
            "total_portfolio_value": round(total_value, 2),
            "positions": positions
        }
        
        print(f"✅ Retrieved {len(positions)} portfolio positions for user {user_id}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Failed to retrieve portfolio: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


@tool
def get_trade_history(
    user_id: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 100,
    config: RunnableConfig = None
) -> Dict:
    """
    Retrieve trade history for a user.
    
    Args:
        user_id: User identifier (uses config if not provided)
        symbol: Filter by stock symbol
        limit: Maximum number of trades to return
        config: Configuration containing user_id
        
    Returns:
        Dictionary with trade history
    """
    try:
        if not user_id and config:
            user_id = config["configurable"].get("user_id", "default_user")
        elif not user_id:
            user_id = "default_user"
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = ["user_id = ?"]
        params = [user_id]
        
        if symbol:
            where_conditions.append("symbol = ?")
            params.append(symbol.upper())
        
        query = f'''
            SELECT * FROM trade_history 
            WHERE {" AND ".join(where_conditions)}
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        trades = [dict(row) for row in rows]
        
        result = {
            "user_id": user_id,
            "total_trades": len(trades),
            "trades": trades
        }
        
        if symbol:
            result["filtered_by_symbol"] = symbol
        
        print(f"✅ Retrieved {len(trades)} trades for user {user_id}")
        return result
        
    except Exception as e:
        error_msg = f"❌ Failed to retrieve trade history: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


# Database utility functions (not tools, for internal use)
def get_database_stats():
    """Get database statistics for monitoring."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count orders by status
        cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status')
        order_stats = dict(cursor.fetchall())
        
        # Count total positions
        cursor.execute('SELECT COUNT(*) FROM portfolio_positions WHERE shares > 0')
        total_positions = cursor.fetchone()[0]
        
        # Count total trades
        cursor.execute('SELECT COUNT(*) FROM trade_history')
        total_trades = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "order_stats": order_stats,
            "total_positions": total_positions,
            "total_trades": total_trades,
            "database_path": DB_PATH
        }
        
    except Exception as e:
        return {"error": f"Failed to get database stats: {str(e)}"}


if __name__ == "__main__":
    # Test database initialization and basic functionality
    print("🧪 Testing Database Tools...")
    
    # Initialize database (already done on import)
    print(f"📊 Database location: {DB_PATH}")
    
    # Get database stats
    stats = get_database_stats()
    print(f"📈 Database stats: {stats}")
    
    print("✅ Database tools module ready!")
