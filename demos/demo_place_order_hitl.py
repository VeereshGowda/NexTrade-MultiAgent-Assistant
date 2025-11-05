#!/usr/bin/env python3
"""
Test script for place_order tool with Human-in-the-Loop (HITL) functionality.

This script demonstrates how the halt_on_risky_tools function intercepts
trading operations and requires human approval before execution.
"""

import sys
import os
from typing import Dict, Any
from unittest.mock import Mock, patch
import uuid

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_core.messages import AIMessage, ToolMessage
from src.agent.tools import place_order, halt_on_risky_tools, RISKY_TOOLS

def create_mock_state_with_tool_call(
    symbol: str = "AAPL",
    action: str = "buy", 
    shares: int = 10,
    limit_price: float = 150.0,
    order_type: str = "limit"
) -> Dict[str, Any]:
    """
    Create a mock state with a place_order tool call for testing.
    
    Args:
        symbol: Stock symbol (e.g., "AAPL")
        action: "buy" or "sell"
        shares: Number of shares
        limit_price: Price per share
        order_type: Order type (default "limit")
        
    Returns:
        Mock state dictionary with AIMessage containing tool call
    """
    tool_call_id = str(uuid.uuid4())
    
    # Create a tool call that matches the place_order signature
    tool_call = {
        "id": tool_call_id,
        "name": "place_order",
        "args": {
            "symbol": symbol,
            "action": action,
            "shares": shares,
            "limit_price": limit_price,
            "order_type": order_type
        }
    }
    
    # Create AIMessage with the tool call
    ai_message = AIMessage(
        content="Placing order as requested",
        tool_calls=[tool_call]
    )
    
    # Return mock state
    return {
        "messages": [ai_message]
    }

def test_place_order_tool_directly():
    """Test the place_order tool directly without HITL."""
    print("🧪 Testing place_order tool directly (without HITL)")
    print("=" * 60)
    
    # Test valid order using proper tool invocation
    order_params = {
        "symbol": "NVDA",
        "action": "buy",
        "shares": 5,
        "limit_price": 180.50,
        "order_type": "limit"
    }
    
    result = place_order.invoke(order_params)
    
    print(f"✅ Direct tool result: {result}")
    print(f"📊 Order details:")
    print(f"   Symbol: {result['symbol']}")
    print(f"   Action: {result['action']}")
    print(f"   Shares: {result['shares']}")
    print(f"   Price: ${result['limit_price']}")
    print(f"   Total: ${result['total_spent']}")
    print(f"   Status: {result['status']}")
    print()

def test_hitl_approval_scenario():
    """Test HITL with simulated approval."""
    print("🧪 Testing HITL with simulated APPROVAL")
    print("=" * 60)
    
    # Create mock state with place_order tool call
    state = create_mock_state_with_tool_call(
        symbol="TSLA",
        action="buy",
        shares=3,
        limit_price=420.00
    )
    
    # Mock the interrupt function to simulate approval
    with patch('src.agent.tools.interrupt') as mock_interrupt:
        mock_interrupt.return_value = {"approved": True}
        
        result = halt_on_risky_tools(state)
        
        print(f"✅ HITL result (approved): {result}")
        print("📝 Expected behavior: Empty dict (allows tool execution to continue)")
        print(f"🔍 Mock interrupt was called: {mock_interrupt.called}")
        if mock_interrupt.called:
            call_args = mock_interrupt.call_args[0][0]
            print(f"📋 Interrupt called with: {call_args['message']}")
    print()

def test_hitl_rejection_scenario():
    """Test HITL with simulated rejection."""
    print("🧪 Testing HITL with simulated REJECTION")
    print("=" * 60)
    
    # Create mock state with place_order tool call
    state = create_mock_state_with_tool_call(
        symbol="AMZN",
        action="sell",
        shares=50,
        limit_price=3500.00
    )
    
    # Mock the interrupt function to simulate rejection
    with patch('src.agent.tools.interrupt') as mock_interrupt:
        mock_interrupt.return_value = {"approved": False}
        
        result = halt_on_risky_tools(state)
        
        print(f"❌ HITL result (rejected): {result}")
        print("📝 Expected behavior: Dict with cancellation message")
        if "messages" in result and result["messages"]:
            tool_message = result["messages"][0]
            print(f"🛑 Cancellation message: {tool_message.content[:100]}...")
            print(f"🔧 Tool call ID: {tool_message.tool_call_id}")
        print(f"🔍 Mock interrupt was called: {mock_interrupt.called}")
    print()

def test_hitl_with_different_orders():
    """Test HITL with various order types and amounts."""
    print("🧪 Testing HITL with different order scenarios")
    print("=" * 60)
    
    test_scenarios = [
        {
            "name": "Small Buy Order",
            "symbol": "MSFT",
            "action": "buy",
            "shares": 1,
            "limit_price": 350.00
        },
        {
            "name": "Large Sell Order",
            "symbol": "GOOGL",
            "action": "sell", 
            "shares": 100,
            "limit_price": 2800.00
        },
        {
            "name": "Penny Stock Purchase",
            "symbol": "XYZ",
            "action": "buy",
            "shares": 1000,
            "limit_price": 2.50
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['name']}")
        
        state = create_mock_state_with_tool_call(**{k: v for k, v in scenario.items() if k != "name"})
        
        # Simulate approval for odd scenarios, rejection for even
        approved = (i % 2 == 0)
        
        with patch('src.agent.tools.interrupt') as mock_interrupt:
            mock_interrupt.return_value = {"approved": approved}
            
            result = halt_on_risky_tools(state)
            total_cost = scenario["shares"] * scenario["limit_price"]
            
            print(f"   📊 Order: {scenario['action'].upper()} {scenario['shares']} shares of {scenario['symbol']} at ${scenario['limit_price']} (Total: ${total_cost})")
            print(f"   🔄 Decision: {'✅ APPROVED' if approved else '❌ REJECTED'}")
            print(f"   📤 Result: {'Continue execution' if not result else 'Blocked with cancellation message'}")

def test_non_risky_tool_passthrough():
    """Test that non-risky tools pass through without HITL."""
    print("\n🧪 Testing non-risky tool passthrough")
    print("=" * 60)
    
    # Create state with a non-risky tool call
    tool_call = {
        "id": str(uuid.uuid4()),
        "name": "fetch_stock_data",  # This is not in RISKY_TOOLS
        "args": {"stock_symbol": "AAPL"}
    }
    
    ai_message = AIMessage(
        content="Fetching stock data",
        tool_calls=[tool_call]
    )
    
    state = {"messages": [ai_message]}
    
    result = halt_on_risky_tools(state)
    
    print(f"✅ Non-risky tool result: {result}")
    print("📝 Expected behavior: Empty dict (no intervention needed)")
    print(f"🔍 RISKY_TOOLS list: {RISKY_TOOLS}")
    print()

def interactive_hitl_demo():
    """Interactive demonstration of HITL functionality."""
    print("🎮 Interactive HITL Demo")
    print("=" * 60)
    print("This will demonstrate real human approval prompts.")
    print("You'll be asked to approve or reject trading orders.")
    print()
    
    # Create a sample order
    state = create_mock_state_with_tool_call(
        symbol="AAPL",
        action="buy",
        shares=10,
        limit_price=175.00
    )
    
    print("🚀 Simulating Portfolio Agent placing an order...")
    print("📞 This would normally trigger the interrupt mechanism in a real graph execution.")
    
    # In a real scenario, this would trigger the actual interrupt
    # For demo purposes, we'll show what the approval prompt would look like
    args = state["messages"][-1].tool_calls[0]["args"]
    total_cost = args["shares"] * args["limit_price"]
    
    print(f"\n🚨 HUMAN APPROVAL REQUIRED 🚨")
    print(f"Trading Action: {args['action'].upper()} {args['shares']} shares of {args['symbol']} at ${args['limit_price']} per share (Total: ${total_cost})")
    print(f"Tool: place_order")
    
    # Simulate user input
    user_input = input("\n👤 Do you approve this trade? (y/n): ").lower().strip()
    
    if user_input == 'y':
        print("✅ Order approved! In a real system, the trade would execute.")
        # Simulate tool execution
        result = place_order.invoke(args)
        print(f"📊 Trade result: {result}")
    else:
        print("❌ Order rejected! Trade cancelled.")
        print("🛑 Portfolio Agent would receive cancellation message.")

def main():
    """Run all test scenarios."""
    print("🚀 Place Order Tool with HITL Testing Suite")
    print("=" * 70)
    print()
    
    try:
        # Test the tool directly
        test_place_order_tool_directly()
        
        # Test HITL approval
        test_hitl_approval_scenario()
        
        # Test HITL rejection  
        test_hitl_rejection_scenario()
        
        # Test various scenarios
        test_hitl_with_different_orders()
        
        # Test non-risky tool passthrough
        test_non_risky_tool_passthrough()
        
        print("\n🎯 All automated tests completed!")
        print("\nWould you like to try the interactive demo? (y/n): ", end="")
        
        choice = input().lower().strip()
        if choice == 'y':
            interactive_hitl_demo()
        
        print("\n✅ Testing suite completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
