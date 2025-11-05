#!/usr/bin/env python3
"""
Quick environment and API key validation script.
Run this first to ensure everything is set up correctly.
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking Environment Setup...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Required API keys
    required_vars = {
        "Azure OpenAI": {
            "AZURE_OPENAI_API_KEY": "Azure OpenAI API Key",
            "AZURE_OPENAI_ENDPOINT": "Azure OpenAI Endpoint",
            "OPENAI_API_VERSION": "API Version (optional)",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "Deployment Name (optional)"
        },
        "Alternative - Groq": {
            "GROQ_API_KEY": "Groq API Key"
        },
        "Tools": {
            "TAVILY_API_KEY": "Tavily Search API Key",
            "ALPHAVANTAGE_API_KEY": "AlphaVantage Stock API Key"
        },
        "Optional - Tracking": {
            "LANGSMITH_API_KEY": "LangSmith API Key (optional)",
            "LANGSMITH_PROJECT": "LangSmith Project (optional)"
        }
    }
    
    all_good = True
    
    for category, vars_dict in required_vars.items():
        print(f"\n📂 {category}:")
        category_good = True
        
        for var_name, description in vars_dict.items():
            value = os.getenv(var_name)
            if value:
                # Show partial key for security
                if "key" in var_name.lower() or "api" in var_name.lower():
                    display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                else:
                    display_value = value[:50] + "..." if len(value) > 50 else value
                print(f"  ✅ {var_name}: {display_value}")
            else:
                if "optional" not in description.lower():
                    print(f"  ❌ {var_name}: NOT SET")
                    category_good = False
                    all_good = False
                else:
                    print(f"  ⚪ {var_name}: NOT SET (optional)")
        
        if category == "Azure OpenAI" and category_good:
            print("  🎯 Recommended: Use Azure OpenAI for best compatibility")
        elif category == "Alternative - Groq" and os.getenv("GROQ_API_KEY"):
            print("  🔄 Fallback: Groq available as alternative")
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("✅ Environment setup looks good!")
        print("\n🚀 You can now run the main test script:")
        print("   python test_agents.py")
    else:
        print("❌ Some required environment variables are missing.")
        print("\n💡 To fix this:")
        print("1. Check your .env file in the project root")
        print("2. Make sure you have at least Azure OpenAI OR Groq configured")
        print("3. Ensure Tavily and AlphaVantage keys are set")
        
    return all_good

def test_imports():
    """Test if all required packages can be imported."""
    print("\n🧪 Testing Package Imports...")
    print("=" * 40)
    
    packages = [
        ("langchain_core", "LangChain Core"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_groq", "LangChain Groq"),
        ("langchain_tavily", "LangChain Tavily"),
        ("langgraph", "LangGraph"),
        ("streamlit", "Streamlit"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("yfinance", "Yahoo Finance"),
        ("requests", "Requests"),
        ("dotenv", "Python-dotenv"),
        ("pytest", "Pytest")
    ]
    
    all_imported = True
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {description}: Available")
        except ImportError:
            print(f"❌ {description}: Missing")
            all_imported = False
    
    if all_imported:
        print("\n✅ All packages imported successfully!")
    else:
        print("\n❌ Some packages are missing. Install them with:")
        print("   uv pip install -e .")
        
    return all_imported

def check_project_structure():
    """Check if key project files and directories exist."""
    print("\n📁 Checking Project Structure...")
    print("=" * 40)
    
    required_items = [
        ("src/agent/graph.py", "Multi-agent supervisor"),
        ("src/agent/tools.py", "Agent tools"),
        ("src/agent/database_tools.py", "Database tools"),
        ("src/api.py", "FastAPI backend"),
        ("streamlit_app.py", "Streamlit UI"),
        ("data", "Data directory"),
        ("tests", "Test directory"),
        (".env", "Environment configuration")
    ]
    
    all_exist = True
    
    for item, description in required_items:
        exists = os.path.exists(item) or os.path.isdir(item)
        if exists:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing ({item})")
            all_exist = False
    
    if all_exist:
        print("\n✅ Project structure looks good!")
    else:
        print("\n❌ Some required files are missing.")
        
    return all_exist

def check_database():
    """Check if database can be accessed."""
    print("\n🗄️ Checking Database...")
    print("=" * 40)
    
    try:
        import sqlite3
        db_path = "data/trading_orders.db"
        
        if os.path.exists(db_path):
            print(f"✅ Database file exists: {db_path}")
            
            # Try to connect
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if orders table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if cursor.fetchone():
                print("✅ Database schema initialized")
            else:
                print("⚪ Database exists but schema not initialized (will auto-create)")
            
            conn.close()
            return True
        else:
            print(f"⚪ Database will be created on first run: {db_path}")
            return True
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Multi-Agent System Environment Check")
    print("=" * 50)
    
    # Check if running in virtual environment
    import sys
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
    else:
        print("⚠️  WARNING: Virtual environment is NOT active!")
        print("   Please activate it first:")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Linux/Mac: source .venv/bin/activate")
        print("")
    
    print("=" * 50)
    
    env_ok = check_environment()
    imports_ok = test_imports()
    structure_ok = check_project_structure()
    db_ok = check_database()
    
    print("\n" + "=" * 50)
    print("📊 ENVIRONMENT SUMMARY:")
    print("=" * 50)
    
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ ISSUES'}")
    print(f"Package Imports: {'✅ OK' if imports_ok else '❌ ISSUES'}")
    print(f"Project Structure: {'✅ OK' if structure_ok else '❌ ISSUES'}")
    print(f"Database: {'✅ OK' if db_ok else '❌ ISSUES'}")
    
    if env_ok and imports_ok and structure_ok and db_ok:
        print("\n🎉 Everything looks good! You're ready to start.")
        print("\nNext steps (ensure virtual environment is active):")
        print("1. Direct Mode: streamlit run streamlit_app.py")
        print("2. API Mode:")
        print("   - Terminal 1: cd src && python -m uvicorn api:app --reload")
        print("   - Terminal 2: streamlit run streamlit_app.py")
        print("3. Run tests: pytest -v")
    else:
        print("\n⚠️ Please fix the issues above before starting.")
        print("\n💡 Common fixes:")
        print("1. Activate virtual environment:")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Linux/Mac: source .venv/bin/activate")
        print("2. Install dependencies: uv pip install -e .")
        print("3. Create .env file: cp .env.example .env")
        print("4. Add your API keys to .env")
