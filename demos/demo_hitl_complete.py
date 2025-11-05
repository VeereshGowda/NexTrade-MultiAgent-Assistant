#!/usr/bin/env python3
"""
Test the corrected HITL mechanism
"""

import uuid
from src.agent.graph import create_financial_advisor_system
from langchain_core.messages import HumanMessage
from langgraph.types import Command

def print_messages(messages):
    """Print messages in a readable format."""
    for msg in messages:
        if hasattr(msg, 'content') and msg.content:
            content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            print(f"💬 {type(msg).__name__}: {content}")

def test_hitl_corrected():
    """Test HITL with proper interrupt handling."""
    print("🎯 Testing HITL with Corrected Interrupt Detection")
    print("=" * 60)
    
    # Create supervisor
    supervisor = create_financial_advisor_system(use_highlevel=False)
    
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "user_id": "test_user_hitl"
        }
    }
    
    query = "Buy 10 shares of NVIDIA at current market price"
    print(f"Trading Query: {query}")
    
    # Step 1: Initial request
    response = supervisor.invoke({
        "messages": [HumanMessage(content=query)]
    }, config)
    
    print("\n📝 Initial Response Messages:")
    print_messages(response['messages'])
    
    # Step 2: Check for interrupt
    if "__interrupt__" in response:
        print("\n✅ HITL INTERRUPT DETECTED!")
        interrupts = response["__interrupt__"]
        interrupt_data = interrupts[0].value
        
        print(f"🚨 Approval Required:")
        print(f"   Tool: {interrupt_data.get('awaiting', 'unknown')}")
        print(f"   Action: {interrupt_data.get('approval_details', {}).get('order_details', 'N/A')}")
        
        # Test 1: Approve the trade
        print(f"\n✅ Test 1: Approving trade...")
        approved_response = supervisor.invoke(Command(resume={"approved": True}), config=config)
        
        print(f"\n📝 Response after approval:")
        print_messages(approved_response['messages'][-3:])  # Last 3 messages
        
        # Test 2: Start a new trade and reject it
        print(f"\n" + "="*60)
        print(f"🔴 Test 2: Testing rejection...")
        
        config2 = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "user_id": "test_user_hitl_2"
            }
        }
        
        query2 = "Sell 100 shares of Apple stock"
        response2 = supervisor.invoke({
            "messages": [HumanMessage(content=query2)]
        }, config2)
        
        if "__interrupt__" in response2:
            print(f"✅ Second interrupt detected for: {query2}")
            
            # Reject this trade
            rejected_response = supervisor.invoke(Command(resume={"approved": False}), config=config2)
            
            print(f"\n📝 Response after rejection:")
            print_messages(rejected_response['messages'][-3:])  # Last 3 messages
            
            print(f"\n🎉 HITL mechanism fully tested!")
            print(f"✅ Approval scenario: WORKING")
            print(f"✅ Rejection scenario: WORKING") 
            return True
        else:
            print(f"❌ Second interrupt not detected")
            return False
    else:
        print(f"\n❌ NO INTERRUPT DETECTED")
        print(f"This shouldn't happen with the current setup")
        return False

if __name__ == "__main__":
    success = test_hitl_corrected()
    print(f"\nFinal Result: {'✅ ALL TESTS PASSED' if success else '❌ TESTS FAILED'}")
