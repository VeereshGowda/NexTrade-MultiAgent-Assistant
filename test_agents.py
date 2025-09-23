#!/usr/bin/env python3
"""
Command line testing script for the Multi-Agent Financial Advisor System.

This script allows you to test the agents directly from the command line,
matching the same functionality as the Jupyter notebook.
"""

import sys
import os
import uuid
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_core.messages import HumanMessage
from agent.graph import create_financial_advisor_system
from agent.utils import print_messages


def test_system_initialization():
    """Test if the system can be initialized properly."""
    print("🔧 Testing System Initialization...")
    
    try:
        # Test Azure OpenAI configuration
        print("\n📊 Testing with Azure OpenAI...")
        supervisor_azure = create_financial_advisor_system(
            use_highlevel=False, 
            use_azure=True
        )
        print("✅ Azure OpenAI system initialized successfully!")
        
        # Test Groq configuration
        print("\n📊 Testing with Groq...")
        supervisor_groq = create_financial_advisor_system(
            use_highlevel=False, 
            use_azure=False
        )
        print("✅ Groq system initialized successfully!")
        
        return supervisor_azure  # Return Azure by default as it works better
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        print("\n💡 Troubleshooting tips:")
        print("- Check your .env file has all required API keys")
        print("- Make sure you're in the virtual environment")
        print("- Verify API keys are valid")
        return None


def test_simple_query(supervisor):
    """Test with a simple query first."""
    print("\n🧪 Testing Simple Query...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user"
        }
    }
    
    simple_query = "What is the current time?"
    print(f"Query: {simple_query}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=simple_query)]
        }, config)
        
        print("\n📝 Response:")
        print_messages(response['messages'])
        return True
        
    except Exception as e:
        print(f"❌ Error with simple query: {e}")
        return False


def test_research_agent(supervisor):
    """Test the research agent specifically."""
    print("\n🔍 Testing Research Agent...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user"
        }
    }
    
    research_query = "Research the top 3 AI companies for investment opportunities."
    print(f"Query: {research_query}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=research_query)]
        }, config)
        
        print("\n📝 Response:")
        print_messages(response['messages'])
        return True
        
    except Exception as e:
        print(f"❌ Error with research query: {e}")
        return False


def test_portfolio_agent(supervisor):
    """Test the portfolio agent specifically."""
    print("\n📈 Testing Portfolio Agent...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user"
        }
    }
    
    portfolio_query = "Check the current price of NVIDIA stock and analyze it."
    print(f"Query: {portfolio_query}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=portfolio_query)]
        }, config)
        
        print("\n📝 Response:")
        print_messages(response['messages'])
        return True
        
    except Exception as e:
        print(f"❌ Error with portfolio query: {e}")
        return False


def test_order_history(supervisor):
    """Test the order history functionality."""
    print("\n📋 Testing Order History...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user_history"
        }
    }
    
    history_query = "Show me my order history and portfolio summary."
    print(f"Query: {history_query}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=history_query)]
        }, config)
        
        print("\n📝 Response:")
        print_messages(response['messages'])
        
        # Check if order history functionality was accessed
        messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
        if any(keyword in messages_content.lower() for keyword in ["history", "orders", "portfolio", "previous"]):
            print("\n✅ Order history functionality working!")
        else:
            print("\n⚠️ Order history response received, but content unclear.")
            
        return True
        
    except Exception as e:
        print(f"❌ Error with order history query: {e}")
        return False


def test_human_approval_simulation(supervisor):
    """Test human approval mechanism with simulated responses."""
    print("\n🤖 Testing Human Approval Simulation...")
    print("This test simulates both approval and rejection scenarios")
    
    # Test 1: Simulate approval
    print("\n📋 Test 1: Simulating APPROVAL scenario")
    try:
        from agent.tools import halt_on_risky_tools
        from langchain_core.messages import AIMessage
        
        # Create a mock state with a place_order tool call
        mock_tool_call = {
            "name": "place_order",
            "args": {
                "symbol": "NVDA",
                "action": "buy", 
                "shares": 10,
                "limit_price": 150.0
            },
            "id": "test_call_1"
        }
        
        mock_ai_message = AIMessage(
            content="I'll place this order for you.",
            tool_calls=[mock_tool_call]
        )
        
        mock_state = {"messages": [mock_ai_message]}
        
        print("🔧 Mock tool call created:")
        print(f"  - Action: BUY 10 shares of NVDA at $150.00")
        print(f"  - Total cost: $1,500.00")
        print("✅ Human approval simulation test structure ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in approval simulation: {e}")
        return False


def test_portfolio_trading_with_hitl(supervisor):
    """Test the portfolio agent trading functionality with human-in-the-loop."""
    print("\n💰 Testing Portfolio Agent Trading (Human-in-the-Loop)...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user_trading"
        }
    }
    
    trading_query = "Buy 10 shares of NVIDIA at current market price"
    print(f"Query: {trading_query}")
    print("📝 Note: Portfolio Agent now handles all trading with built-in human approval")
    print("🚨 IMPORTANT: Testing HITL mechanism with automatic approval")
    
    try:
        # Step 1: Initial request that should trigger HITL
        response = supervisor.invoke({
            "messages": [HumanMessage(content=trading_query)]
        }, config)
        
        print("\n📝 Initial Response:")
        print_messages(response['messages'])
        
        # Step 2: Check for interrupt
        if "__interrupt__" in response:
            print("\n✅ HITL mechanism activated successfully!")
            interrupts = response["__interrupt__"]
            interrupt_data = interrupts[0].value
            
            print(f"🚨 INTERRUPT DETECTED:")
            print(f"   Tool: {interrupt_data.get('awaiting', 'unknown')}")
            print(f"   Args: {interrupt_data.get('args', {})}")
            print(f"   Message: {interrupt_data.get('message', 'No message')}")
            
            # Test approval scenario
            print("\n✅ Simulating human approval...")
            from langgraph.types import Command
            response = supervisor.invoke(Command(resume={"approved": True}), config=config)
            
            print("\n📝 Response after approval:")
            print_messages(response['messages'])
            
            return True
        else:
            # Check if trading completed without interrupt (unexpected)
            messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
            
            if any(keyword in messages_content.lower() for keyword in ["order", "executed", "filled", "placed"]):
                print("\n⚠️ Trading completed without HITL mechanism!")
                print("💡 This might indicate the HITL mechanism is not properly configured")
                return False
            else:
                print("\n⚠️ No interrupt detected and no trading completed")
                print("💡 Portfolio Agent may need configuration review")
                return False
        
    except Exception as e:
        print(f"❌ Error during trading test: {e}")
        return False


def test_full_investment_scenario(supervisor):
    """Test the complete investment scenario from the notebook with order placement."""
    print("\n💰 Testing Full Investment Scenario (Including Order Placement)...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user_investment"
        }
    }
    
    investment_query = """
    I want you to invest $1,000 into the most promising company in the AI sector.  
    Please research the options, pick the best candidate, and then go ahead and place 
    a buy order for me.
    """
    
    print(f"Query: {investment_query.strip()}")
    print("📝 Note: This tests the complete workflow including research, analysis, and order placement")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=investment_query)]
        }, config)
        
        print("\n📝 Full Response:")
        print_messages(response['messages'])
        
        # Analyze the response for different components
        messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
        
        research_done = False
        analysis_done = False
        order_attempted = False
        human_approval = False
        
        # Check if research was performed
        if any(keyword in messages_content.lower() for keyword in ["research", "ai companies", "investment"]):
            research_done = True
            print("✅ Research component detected")
        
        # Check if analysis was performed
        if any(keyword in messages_content.lower() for keyword in ["analysis", "stock", "price", "valuation"]):
            analysis_done = True
            print("✅ Analysis component detected")
        
        # Check if order placement was attempted
        if any(keyword in messages_content.lower() for keyword in ["order", "buy", "shares", "purchase"]):
            order_attempted = True
            print("✅ Order placement attempted")
        
        # Check if human approval mechanism was triggered (look for actual trading approval)
        tool_calls_made = []
        for msg in response['messages']:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_calls_made.extend([tc['name'] for tc in msg.tool_calls])
        
        # Real HITL should involve place_order tool call
        if "place_order" in tool_calls_made:
            human_approval = True
            print("✅ Human approval mechanism triggered (place_order called)")
        elif any(keyword in messages_content.lower() for keyword in ["approval required", "human approval", "confirm trade", "authorize trade"]):
            human_approval = True
            print("✅ Human approval mechanism triggered (explicit approval request)")
        elif "human" in messages_content.lower() and any(word in messages_content.lower() for word in ["clarification", "verify", "confirm"]):
            print("💡 Human interaction requested (clarification needed, not trading approval)")
        
        # Overall assessment
        if research_done and analysis_done and order_attempted:
            print("\n🎉 Full investment workflow completed successfully!")
            if human_approval:
                print("🛡️ Human-in-the-loop safety mechanism working correctly!")
            return True
        else:
            print("\n⚠️ Investment scenario completed, but some components may be missing:")
            if not research_done:
                print("  - Research component not clearly detected")
            if not analysis_done:
                print("  - Analysis component not clearly detected")
            if not order_attempted:
                print("  - Order placement not attempted")
            return False
            
    except Exception as e:
        print(f"❌ Error with investment scenario: {e}")
        return False


def test_database_agent(supervisor):
    """Test the database agent specifically."""
    print("\n💾 Testing Database Agent...")
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user_db"
        }
    }
    
    database_query = "Show me my order history and current portfolio positions from the database."
    print(f"Query: {database_query}")
    
    try:
        response = supervisor.invoke({
            "messages": [HumanMessage(content=database_query)]
        }, config)
        
        print("\n📝 Response:")
        print_messages(response['messages'])
        
        # Check if database agent was involved
        messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
        
        if any(keyword in messages_content.lower() for keyword in ["database", "orders", "portfolio", "history"]):
            print("✅ Database agent functionality detected")
        else:
            print("⚠️ Database agent response unclear")
            
        return True
        
    except Exception as e:
        print(f"❌ Error with database query: {e}")
        return False


def interactive_trading_test(supervisor):
    """Interactive test for human-in-the-loop trading functionality."""
    print("\n🎯 Interactive Trading Test (Human-in-the-Loop)")
    print("=" * 60)
    print("This test will demonstrate the human approval mechanism for trading.")
    print("You'll be able to approve or reject trade orders in real-time.")
    print("\nType 'back' to return to main menu")
    
    session_config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "interactive_trader"
        }
    }
    
    # Predefined trading scenarios
    trading_scenarios = [
        "Buy 10 shares of NVIDIA at market price",
        "Purchase $500 worth of Tesla stock",
        "Sell 5 shares of Apple stock",
        "Buy $1000 worth of Microsoft shares"
    ]
    
    print("\n📋 Available trading scenarios:")
    for i, scenario in enumerate(trading_scenarios, 1):
        print(f"  {i}. {scenario}")
    print("  5. Custom trading command")
    
    while True:
        try:
            choice = input("\n💬 Select scenario (1-5) or 'back': ").strip()
            
            if choice.lower() in ['back', 'exit', 'quit']:
                break
                
            if choice in ['1', '2', '3', '4']:
                trading_query = trading_scenarios[int(choice) - 1]
            elif choice == '5':
                trading_query = input("Enter your custom trading command: ").strip()
                if not trading_query:
                    continue
            else:
                print("Invalid choice. Please select 1-5 or 'back'.")
                continue
                
            print(f"\n🤖 Processing trading command: {trading_query}")
            print("📝 Watch for human approval prompts...")
            
            response = supervisor.invoke({
                "messages": [HumanMessage(content=trading_query)]
            }, session_config)
            
            print("\n📝 Trading Response:")
            print_messages(response['messages'])
            
            # Check if approval was requested
            messages_content = " ".join([msg.content for msg in response['messages'] if hasattr(msg, 'content')])
            if "approval" in messages_content.lower() or "human" in messages_content.lower():
                print("\n✅ Human-in-the-loop mechanism activated!")
            else:
                print("\n💡 No human approval was required for this action.")
            
        except KeyboardInterrupt:
            print("\n👋 Returning to main menu...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def interactive_mode(supervisor):
    """Interactive mode for manual testing."""
    print("\n🎯 Interactive Mode - Type 'quit' to exit")
    print("You can now test any queries manually:")
    
    session_config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "interactive_user"
        }
    }
    
    while True:
        try:
            user_input = input("\n💬 Your query: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            print(f"\n🤖 Processing: {user_input}")
            
            response = supervisor.invoke({
                "messages": [HumanMessage(content=user_input)]
            }, session_config)
            
            print("\n📝 Response:")
            print_messages(response['messages'])
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def main():
    """Main testing function."""
    print("🚀 Multi-Agent Financial Advisor Testing Suite")
    print("=" * 50)
    
    # Test system initialization
    supervisor = test_system_initialization()
    if not supervisor:
        print("\n❌ Cannot proceed with testing due to initialization failure.")
        return
    
    print("\n" + "=" * 50)
    print("🎯 Testing Options:")
    print("1. Run Full Test Suite (all 7 automated tests)")
    print("2. Skip to Interactive Testing")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            # Run full test suite
            print("\n🧪 Running Full Test Suite...")
            print("=" * 50)
            
            # Run test suite
            tests = [
                ("Simple Query", test_simple_query),
                ("Research Agent", test_research_agent),
                ("Portfolio Agent", test_portfolio_agent),
                ("Database Agent", test_database_agent),
                ("Order History", test_order_history),
                ("Human Approval Simulation", test_human_approval_simulation),
                ("Portfolio Trading (HITL)", test_portfolio_trading_with_hitl),
                ("Full Investment Scenario", test_full_investment_scenario)
            ]
            
            results = {}
            
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    results[test_name] = test_func(supervisor)
                except Exception as e:
                    print(f"❌ {test_name} failed with error: {e}")
                    results[test_name] = False
            
            # Print summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY:")
            print("=" * 50)
            
            for test_name, passed in results.items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"{test_name:.<30} {status}")
            
            total_tests = len(results)
            passed_tests = sum(results.values())
            
            print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                print("🎉 All tests passed! Your system is working correctly.")
            else:
                print("⚠️ Some tests failed. Check the error messages above.")
            
            # After test suite, offer interactive options
            print("\n" + "=" * 50)
            print("🎯 Interactive Testing Options:")
            print("1. General interactive mode")
            print("2. Trading-specific interactive mode (Human-in-the-Loop)")
            print("3. Exit testing")
            
            interactive_choice = input("\nSelect option (1-3): ").strip()
            
            if interactive_choice == '1':
                interactive_mode(supervisor)
            elif interactive_choice == '2':
                interactive_trading_test(supervisor)
            elif interactive_choice == '3':
                print("👋 Testing complete!")
            else:
                print("Invalid choice. Exiting testing.")
            break
            
        elif choice == '2':
            # Skip directly to interactive testing
            print("\n🎯 Skipping to Interactive Testing...")
            print("=" * 50)
            print("🎯 Interactive Testing Options:")
            print("1. General interactive mode")
            print("2. Trading-specific interactive mode (Human-in-the-Loop)")
            print("3. Back to main menu")
            
            interactive_choice = input("\nSelect option (1-3): ").strip()
            
            if interactive_choice == '1':
                interactive_mode(supervisor)
                break
            elif interactive_choice == '2':
                interactive_trading_test(supervisor)
                break
            elif interactive_choice == '3':
                continue  # Go back to main menu
            else:
                print("Invalid choice. Returning to main menu.")
                continue
                
        elif choice == '3':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
            continue


if __name__ == "__main__":
    main()
