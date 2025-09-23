"""
Streamlit Multi-Agent Supervisor System with Portfolio-Based Trading.
"""

import streamlit as st
import sys
import os
import uuid
from datetime import datetime
import base64
from io import BytesIO

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_core.messages import HumanMessage
from agent.graph import (
    create_financial_advisor_system, 
    create_research_agent,
    create_portfolio_agent, 
    create_database_agent,
    save_all_graph_visualizations
)
from agent.context import get_default_config
from agent.utils import print_messages, save_graph_image, get_graph_image_bytes


def process_message(supervisor, prompt, user_id, thread_id):
    """Process a message through the supervisor and return the response."""
    try:
        # Create configuration
        config = {
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id
            }
        }
        
        # Get response from supervisor
        response = supervisor.invoke({
            "messages": [HumanMessage(content=prompt)]
        }, config)
        
        # Check for interrupt (HITL approval needed)
        if "__interrupt__" in response:
            interrupts = response["__interrupt__"]
            if interrupts:
                interrupt_data = interrupts[0].value
                return {
                    "type": "approval_needed",
                    "approval_details": interrupt_data["approval_details"],
                    "config": config
                }
        
        # Extract the final response (no approval needed)
        final_message = response['messages'][-1]
        response_content = final_message.content
        
        return {
            "type": "success",
            "content": response_content
        }
        
    except Exception as e:
        error_details = {
            "type": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        # Add specific troubleshooting for common issues
        if "tool" in str(e).lower():
            error_details["troubleshooting"] = "This appears to be a tool-related error. Try switching to Azure OpenAI in the sidebar."
        elif "api" in str(e).lower():
            error_details["troubleshooting"] = "API connection issue. Check your API keys and internet connection."
        elif "timeout" in str(e).lower():
            error_details["troubleshooting"] = "Request timed out. Try again or check your connection."
        
        return error_details


def display_graph_image(graph, title):
    """Display graph image in Streamlit with proper sizing."""
    try:
        # Get PNG data using improved method
        png_data = get_graph_image_bytes(graph)
        
        if png_data:
            # Display in Streamlit with controlled width - fixed sizing
            st.image(
                png_data, 
                caption=title, 
                width=600  # Fixed width for better display
            )
            
            # Provide download button
            st.download_button(
                label=f"📥 Download {title} Graph",
                data=png_data,
                file_name=f"{title.lower().replace(' ', '_')}_graph.png",
                mime="image/png",
                help=f"Download the {title} visualization as PNG"
            )
        else:
            st.error(f"❌ Unable to generate visualization for {title}")
            st.info("This might be due to network connectivity issues or missing dependencies.")
            st.info("💡 **Troubleshooting tips:**")
            st.info("• Check your internet connection")
            st.info("• The system will retry with local rendering")
            
    except Exception as e:
        st.error(f"Error displaying {title}: {e}")
        st.info("Please check the terminal for detailed error information.")
        st.info("Try refreshing the page or check your internet connection.")


def main():
    st.set_page_config(
        page_title="NexTrade - Multi Agent AI",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 NexTrade - A Multi Agent AI application to conduct stock market transactions")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Implementation type
        use_highlevel = st.radio(
            "Implementation Type:",
            ["Custom Graph", "High-level API"],
            index=0
        ) == "High-level API"
        
        # Model provider selection
        use_azure = st.radio(
            "Model Provider:",
            ["Azure OpenAI (Recommended)", "Groq"],
            index=0,
            help="Azure OpenAI matches the notebook configuration and should work better"
        ) == "Azure OpenAI (Recommended)"
        
        # User ID for session
        user_id = st.text_input("User ID:", value="streamlit_user")
        
        st.markdown("---")
        st.header("📊 Agent Visualizations")
        
        # Buttons to show individual agent graphs
        if st.button("🔍 Research Agent"):
            st.session_state.show_research = True
        if st.button("📈 Portfolio Agent (with Trading)"):
            st.session_state.show_portfolio = True
        if st.button("💾 Database Agent"):
            st.session_state.show_database = True
        if st.button("🎯 Supervisor System"):
            st.session_state.show_supervisor = True
            
        st.markdown("---")
        st.header("📋 Environment Status")
        
        # Check environment variables
        env_status = {}
        required_vars = {
            "Azure OpenAI": ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"],
            "Groq": ["GROQ_API_KEY"],
            "General": ["TAVILY_API_KEY", "ALPHAVANTAGE_API_KEY"]
        }
        
        for category, vars_list in required_vars.items():
            for var in vars_list:
                value = os.getenv(var)
                if value:
                    st.success(f"✅ {var}")
                else:
                    st.error(f"❌ {var} not set")
        
        st.markdown("---")
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.pending_approval = None
            # Also reset supervisor if configuration changed
            if "supervisor" in st.session_state:
                del st.session_state.supervisor
            if "current_config" in st.session_state:
                del st.session_state.current_config
            st.rerun()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "pending_approval" not in st.session_state:
        st.session_state.pending_approval = None
    if "supervisor" not in st.session_state or "current_config" not in st.session_state or \
       st.session_state.current_config != (use_highlevel, use_azure):
        with st.spinner("🚀 Initializing NexTrade Multi-Agent System..."):
            try:
                st.session_state.supervisor = create_financial_advisor_system(
                    use_highlevel=use_highlevel,
                    use_azure=use_azure
                )
                st.session_state.current_config = (use_highlevel, use_azure)
                model_info = "Azure OpenAI" if use_azure else "Groq"
                impl_info = "High-level API" if use_highlevel else "Custom Graph"
                st.success(f"✅ NexTrade Multi-Agent System initialized successfully! Using {model_info} with {impl_info}")
                
                # Display current configuration for debugging
                st.info(f"🔧 Configuration: {model_info} + {impl_info}")
            except Exception as e:
                st.error(f"❌ Error initializing system: {e}")
                st.error("Please check your API keys in the .env file")
                return
    
    # Store user_id in session state for easier access
    if "user_id" not in st.session_state:
        st.session_state.user_id = user_id
    else:
        st.session_state.user_id = user_id  # Update if changed
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with NexTrade AI Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Handle pending approval if exists
        if "pending_approval" in st.session_state and st.session_state.pending_approval:
            approval_data = st.session_state.pending_approval
            
            st.warning("🚨 **Human Approval Required**")
            st.info(f"**Trading Action:** {approval_data['approval_details']['order_details']}")
            
            col_approve, col_reject = st.columns(2)
            
            with col_approve:
                if st.button("✅ Approve Trade", use_container_width=True):
                    with st.spinner("Processing approval..."):
                        try:
                            # Resume with approval
                            from langgraph.types import Command
                            approved_response = st.session_state.supervisor.invoke(
                                Command(resume={"approved": True}), 
                                config=approval_data["config"]
                            )
                            
                            # Extract response
                            final_message = approved_response['messages'][-1]
                            response_content = final_message.content
                            
                            st.success("✅ Trade approved and executed!")
                            st.markdown(response_content)
                            
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response_content
                            })
                            
                            # Clear pending approval
                            del st.session_state.pending_approval
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error processing approval: {e}")
            
            with col_reject:
                if st.button("❌ Reject Trade", use_container_width=True):
                    with st.spinner("Processing rejection..."):
                        try:
                            # Resume with rejection
                            from langgraph.types import Command
                            rejected_response = st.session_state.supervisor.invoke(
                                Command(resume={"approved": False}), 
                                config=approval_data["config"]
                            )
                            
                            # Extract response
                            final_message = rejected_response['messages'][-1]
                            response_content = final_message.content
                            
                            st.info("❌ Trade rejected by user")
                            st.markdown(response_content)
                            
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response_content
                            })
                            
                            # Clear pending approval
                            del st.session_state.pending_approval
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error processing rejection: {e}")
        
        # Chat input (only show if no pending approval)
        if "pending_approval" not in st.session_state or not st.session_state.pending_approval:
            if prompt := st.chat_input("Ask about investments, research, or trading..."):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("🤖 Processing..."):
                        try:
                            # Create configuration
                            config = {
                                "configurable": {
                                    "thread_id": st.session_state.thread_id,
                                    "user_id": st.session_state.user_id
                                }
                            }
                            
                            # Get response from supervisor
                            response = st.session_state.supervisor.invoke({
                                "messages": [HumanMessage(content=prompt)]
                            }, config)
                            
                            # Check for interrupt (HITL approval needed)
                            if "__interrupt__" in response:
                                interrupts = response["__interrupt__"]
                                if interrupts:
                                    interrupt_data = interrupts[0].value
                                    
                                    # Store approval data in session state
                                    st.session_state.pending_approval = {
                                        "approval_details": interrupt_data["approval_details"],
                                        "config": config
                                    }
                                    
                                    st.warning("🚨 **Human Approval Required**")
                                    st.info(f"**Trading Action:** {interrupt_data['approval_details']['order_details']}")
                                    st.info("Please use the approval buttons above to proceed.")
                                    st.rerun()
                                    return
                            
                            # Extract the final response (no approval needed)
                            final_message = response['messages'][-1]
                            response_content = final_message.content
                            
                            st.markdown(response_content)
                            
                            # Add assistant message
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response_content
                            })
                        except Exception as e:
                            error_msg = f"❌ Error generating response: {e}"
                            st.error(error_msg)
                            
                            # Add debugging information
                            st.error("**Debug Information:**")
                            st.error(f"- Error Type: {type(e).__name__}")
                            st.error(f"- Error Details: {str(e)}")
                            
                            # Check if this is a tool-related error
                            if "tool" in str(e).lower():
                                st.error("This appears to be a tool-related error. Common causes:")
                                st.error("- Model provider not supporting the requested tools")
                                st.error("- Try switching to Azure OpenAI in the sidebar")
                                st.error("- Check that all API keys are correctly set in .env file")
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": error_msg
                            })
        else:
            st.info("⏳ Please respond to the pending approval above before submitting a new request.")
    
    with col2:
        st.header("📋 Quick Actions")
        
        if st.button("� Research Investment Ideas"):
            sample_prompt = "Research renewable energy companies and provide investment recommendations without executing any trades."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            
            # Process the message
            with st.spinner("🤖 Researching investment ideas..."):
                result = process_message(
                    st.session_state.supervisor, 
                    sample_prompt, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    if "troubleshooting" in result:
                        error_msg += f"\n💡 {result['troubleshooting']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
                    st.error(f"Error processing request: {result['error_type']}")
                    if "troubleshooting" in result:
                        st.info(result['troubleshooting'])
            st.rerun()
        
        if st.button("📊 Analyze Tesla Stock"):
            sample_prompt = "Can you analyze Tesla (TSLA) stock and provide comprehensive trading recommendations? Please include current stock price, recent price trends, technical analysis, fundamental analysis, market sentiment, and detailed trading recommendations with price targets."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            
            # Process the message
            with st.spinner("🤖 Analyzing Tesla stock..."):
                result = process_message(
                    st.session_state.supervisor, 
                    sample_prompt, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
        
        if st.button("� Execute Sample Investment"):
            sample_prompt = "I want to invest $5,000 in renewable energy companies. Research the options, pick the best candidate, and execute the trade."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            
            # Process the message
            with st.spinner("🤖 Executing investment order..."):
                result = process_message(
                    st.session_state.supervisor, 
                    sample_prompt, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    if "troubleshooting" in result:
                        error_msg += f"\n💡 {result['troubleshooting']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
                    st.error(f"Error processing investment: {result['error_type']}")
                    if "troubleshooting" in result:
                        st.info(result['troubleshooting'])
            st.rerun()
        
        if st.button("�🕒 Current Market Time"):
            sample_prompt = "What is the current time for market analysis?"
            # Add user message
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            
            # Process the message
            with st.spinner("🤖 Getting current time..."):
                result = process_message(
                    st.session_state.supervisor, 
                    sample_prompt, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
        
        if st.button("📈 View Order History"):
            sample_prompt = "Show me my order history and portfolio summary"
            # Add user message
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            
            # Process the message
            with st.spinner("🤖 Retrieving order history..."):
                result = process_message(
                    st.session_state.supervisor, 
                    sample_prompt, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
    
    # Display agent visualizations based on sidebar buttons
    if "show_research" in st.session_state and st.session_state.show_research:
        st.markdown("---")
        st.header("🔍 Research Agent Graph")
        with st.spinner("Generating Research Agent visualization..."):
            research_agent = create_research_agent()
            display_graph_image(research_agent, "Research Agent")
        st.session_state.show_research = False
    
    if "show_portfolio" in st.session_state and st.session_state.show_portfolio:
        st.markdown("---")
        st.header("📈 Portfolio Agent Graph")
        st.info("💡 Portfolio Agent now handles all trading operations with built-in human approval for safety!")
        with st.spinner("Generating Portfolio Agent visualization..."):
            portfolio_agent = create_portfolio_agent()
            display_graph_image(portfolio_agent, "Portfolio Agent")
        st.session_state.show_portfolio = False
    
    if "show_database" in st.session_state and st.session_state.show_database:
        st.markdown("---")
        st.header("💾 Database Agent Graph")
        st.info("💡 Database Agent manages all order storage, portfolio tracking, and historical data!")
        with st.spinner("Generating Database Agent visualization..."):
            database_agent = create_database_agent()
            display_graph_image(database_agent, "Database Agent")
        st.session_state.show_database = False
    
    if "show_supervisor" in st.session_state and st.session_state.show_supervisor:
        st.markdown("---")
        st.header("🎯 Supervisor System Graph")
        
        # Show the existing supervisor_custom.png image
        supervisor_image_path = os.path.join(os.path.dirname(__file__), "images", "supervisor_custom.png")
        if os.path.exists(supervisor_image_path):
            st.image(
                supervisor_image_path,
                caption="Supervisor System - Custom Graph Architecture",
                width=600
            )
            
            # Provide download button for the existing image
            with open(supervisor_image_path, "rb") as file:
                st.download_button(
                    label="📥 Download Supervisor System Graph",
                    data=file.read(),
                    file_name="supervisor_custom.png",
                    mime="image/png",
                    help="Download the Supervisor System visualization as PNG"
                )
        else:
            st.error("❌ Supervisor custom image not found at images/supervisor_custom.png")
            st.info("Falling back to dynamic graph generation...")
            with st.spinner("Generating Supervisor System visualization..."):
                display_graph_image(st.session_state.supervisor, "Supervisor System")
        
        st.session_state.show_supervisor = False
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **📈 NexTrade Multi-Agent System Features:**
    - 🔍 **Research Agent**: Finds investment opportunities and market research
    - 📈 **Portfolio Agent**: Manages portfolio data, investment analysis, AND executes trades with human-in-the-loop safety
    - 💾 **Database Agent**: Stores orders, tracks portfolio positions, and manages historical data in SQLite
    - 🎯 **Supervisor**: Coordinates agents and manages workflow
    
    **🛡️ Safety Features:**
    - Human approval required for all trading operations (built into Portfolio Agent)
    - Real-time market data integration
    - Comprehensive order history tracking in persistent database
    - Portfolio position tracking and analytics
    
    **🔧 Troubleshooting:**
    - If you get tool-related errors, try switching to Azure OpenAI
    - Make sure all required API keys are set in your .env file
    - The system works best with the same configuration as the notebook (Azure OpenAI)
    """)
    
    # Sample test message for easy debugging
    st.markdown("**💡 Quick Tests:**")
    
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        if st.button("🧪 Simple Test"):
            test_message = "What is the current time?"
            # Add user message
            st.session_state.messages.append({"role": "user", "content": test_message})
            
            # Process the message
            with st.spinner("🤖 Running simple test..."):
                result = process_message(
                    st.session_state.supervisor, 
                    test_message, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
            
        if st.button("🔍 Research Test"):
            test_message = "Research the top AI companies for investment."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": test_message})
            
            # Process the message
            with st.spinner("🤖 Running research test..."):
                result = process_message(
                    st.session_state.supervisor, 
                    test_message, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
    
    with col_test2:
        if st.button("📈 Tesla Stock Analysis Test"):
            test_message = "Analyze Tesla (TSLA) stock with current price, trends, and comprehensive trading recommendations."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": test_message})
            
            # Process the message
            with st.spinner("🤖 Running Tesla stock analysis test..."):
                result = process_message(
                    st.session_state.supervisor, 
                    test_message, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()
            
        if st.button("💰 Full Investment Test"):
            test_message = "I want to invest $1,000 into the most promising company in the AI sector. Please research the options, pick the best candidate, and then go ahead and place a buy order for me."
            # Add user message
            st.session_state.messages.append({"role": "user", "content": test_message})
            
            # Process the message
            with st.spinner("🤖 Running full investment test..."):
                result = process_message(
                    st.session_state.supervisor, 
                    test_message, 
                    st.session_state.user_id, 
                    st.session_state.thread_id
                )
                
                if result["type"] == "success":
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["content"]
                    })
                elif result["type"] == "approval_needed":
                    st.session_state.pending_approval = {
                        "approval_details": result["approval_details"],
                        "config": result["config"]
                    }
                else:  # error
                    error_msg = f"❌ Error: {result['error']}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            st.rerun()


if __name__ == "__main__":
    main()
