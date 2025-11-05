#!/usr/bin/env python3
"""
Test script for Database Agent functionality.

This script tests the database tools and Database Agent integration.
"""

import sys
import os
import uuid
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_core.messages import HumanMessage
from agent.graph import create_financial_advisor_system, create_database_agent
from agent.database_tools import get_database_stats
from agent.utils import print_messages


def test_database_tools():
    """Test the database tools directly."""
    print("🧪 Testing Database Tools...")
    
    # Test configuration
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_db_user"
        }
    }
    
    try:
        # Test database stats
        stats = get_database_stats()
        print(f"📊 Database stats: {stats}")
        
        # Test inserting an order
        from agent.database_tools import insert_order
        order_result = insert_order.invoke({
            "symbol": "NVDA",
            "action": "buy", 
            "shares": 10,
            "price": 150.0,
            "order_type": "limit"
        }, config=config)
        print(f"✅ Order insertion result: {order_result}")
        
        # Test retrieving orders
        from agent.database_tools import get_user_orders
        orders_result = get_user_orders.invoke({}, config=config)
        print(f"✅ Retrieved orders: {orders_result}")
        
        # Test portfolio positions
        from agent.database_tools import get_portfolio_positions
        portfolio_result = get_portfolio_positions.invoke({}, config=config)
        print(f"✅ Portfolio positions: {portfolio_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database tools test failed: {e}")
        return False


def test_database_agent():
    """Test the Database Agent through the supervisor."""
    print("\n💾 Testing Database Agent...")
    
    # Create the system
    try:
        supervisor = create_financial_advisor_system()
        print("✅ Financial advisor system with Database Agent created")
    except Exception as e:
        print(f"❌ Failed to create system: {e}")
        return False
    
    # Test configuration
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_db_agent_user"
        }
    }
    
    # Test queries for Database Agent
    test_queries = [
        "Show me my order history",
        "What orders do I have pending?",
        "Display my current portfolio positions",
        "Get my trade history for the last month",
        "Store a new order for 5 shares of Apple at $190",
        "Update my latest order status to filled"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing query: {query}")
        
        try:
            response = supervisor.invoke({
                "messages": [HumanMessage(content=query)]
            }, config)
            
            print("📝 Response:")
            print_messages(response['messages'])
            
            # Check if database agent was involved
            messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
            
            if any(keyword in messages_content.lower() for keyword in ["database", "order", "portfolio", "history"]):
                print("✅ Database Agent appears to be involved")
            else:
                print("⚠️ Database Agent involvement unclear")
                
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return False
    
    return True


def test_database_agent_standalone():
    """Test the Database Agent as a standalone component."""
    print("\n🔧 Testing Database Agent Standalone...")
    
    try:
        database_agent = create_database_agent()
        print("✅ Database Agent created successfully")
        
        # Test configuration
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "user_id": "standalone_test_user"
            }
        }
        
        # Test direct interaction with database agent
        test_query = "Show me all my orders and current portfolio positions"
        
        response = database_agent.invoke({
            "messages": [HumanMessage(content=test_query)]
        }, config)
        
        print("📝 Database Agent Response:")
        print_messages(response['messages'])
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone Database Agent test failed: {e}")
        return False


def test_integration_workflow():
    """Test a complete workflow involving multiple agents including database."""
    print("\n🔄 Testing Integration Workflow...")
    
    # Create the system
    supervisor = create_financial_advisor_system()
    
    # Test configuration
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "integration_test_user"
        }
    }
    
    # Complete workflow test
    workflow_query = """
    I want to buy 10 shares of Tesla. Please:
    1. Look up the current Tesla stock price
    2. Execute the purchase 
    3. Store the order details in the database
    4. Show me my updated portfolio
    """
    
    print(f"📝 Testing integration workflow: {workflow_query.strip()}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=workflow_query)]
        }, config)
        
        print("📝 Integration Workflow Response:")
        print_messages(response['messages'])
        
        # Check if multiple agents were involved
        messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
        
        portfolio_involved = "portfolio" in messages_content.lower()
        database_involved = any(keyword in messages_content.lower() for keyword in ["database", "stored", "order"])
        
        print(f"\n📊 Agent Involvement:")
        print(f"Portfolio Agent: {'✅' if portfolio_involved else '❌'}")
        print(f"Database Agent: {'✅' if database_involved else '❌'}")
        
        if portfolio_involved and database_involved:
            print("✅ Integration workflow completed successfully!")
            return True
        else:
            print("⚠️ Integration workflow may be incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Integration workflow failed: {e}")
        return False


def main():
    """Main testing function for Database Agent."""
    print("🚀 Database Agent Testing Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Database Tools", test_database_tools),
        ("Database Agent (via Supervisor)", test_database_agent),
        ("Database Agent (Standalone)", test_database_agent_standalone),
        ("Integration Workflow", test_integration_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 DATABASE AGENT TEST SUMMARY:")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All Database Agent tests passed!")
        print("\n📝 Next Steps:")
        print("1. Run 'python test_agents.py' to test full system integration")
        print("2. Use Streamlit app to test Database Agent through UI")
        print("3. Check the SQLite database at: data/trading_orders.db")
    else:
        print("⚠️ Some Database Agent tests failed. Check the errors above.")
    
    # Show database location
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'trading_orders.db')
    print(f"\n💾 Database location: {db_path}")
    
    # Show final database stats
    try:
        stats = get_database_stats()
        print(f"📊 Final database stats: {stats}")
    except Exception as e:
        print(f"⚠️ Could not retrieve final database stats: {e}")


if __name__ == "__main__":
    main()
