# NexTrade: Multi-Agent Trading System for Intelligent Stock Market Operations

A sophisticated multi-agent system that automates and optimizes stock market trading operations through intelligent agent coordination, built with LangGraph and featuring human-in-the-loop safety mechanisms.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)

## Overview

NexTrade is a production-ready multi-agent trading system that demonstrates how intelligent agent coordination can enhance financial decision-making while maintaining essential human oversight. The system orchestrates three specialized agents—Research, Portfolio, and Database—under a central supervisor to deliver comprehensive trading workflows from market research to trade execution and portfolio tracking.

![Supervisor System Architecture](images/supervisor_custom.png)

*Figure 1: NexTrade Multi-Agent System Architecture showing the custom supervisor coordinating specialized agents*

### Key Features

- 🤖 **Multi-Agent Architecture**: Specialized agents for research, trading, and data management
- 🛡️ **Human-in-the-Loop Safety**: Mandatory human approval for all trading operations
- 📊 **Real-time Market Data**: Live stock prices and comprehensive market analysis
- 💾 **Persistent Portfolio Tracking**: SQLite database with complete audit trails
- 🔄 **Intelligent Workflow Orchestration**: Automated task delegation and coordination
- 🌐 **Multiple Interfaces**: Command-line tools and Streamlit web application
- 🔧 **Production Ready**: Comprehensive testing suite and error handling

## Target Audience

- **Individual Traders**: Enhanced decision-making tools with automated research
- **Financial Advisors**: Professional portfolio management capabilities
- **AI/ML Engineers**: Reference implementation for multi-agent financial systems
- **Students & Researchers**: Educational platform for learning agentic AI concepts

## Prerequisites

- **Python**: 3.11 or higher
- **uv**: Modern Python package manager ([Install uv](https://docs.astral.sh/uv/getting-started/installation/))
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM recommended
- **Internet Connection**: Required for market data and AI model access
- **API Keys**: Azure OpenAI or Groq account for LLM access

## Installation

### Repository Structure

```
AAIDC-Module2-MultiAgent/
├── README.md                    # Project documentation
├── LICENSE                     # MIT license
├── pyproject.toml              # Python project configuration
├── uv.lock                     # Dependency lock file
├── langgraph.json              # LangGraph configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
├── streamlit_app.py            # Web interface application
├── test_agents.py              # Comprehensive testing suite
├── test_database_agent.py      # Database-specific tests
├── test_hitl_complete.py       # Human-in-the-loop tests
├── test_place_order_hitl.py    # Trading safety tests
├── check_setup.py              # Environment verification
├── Makefile                    # Build automation
├── src/                        # Main source code
│   └── agent/                  # Agent implementation
│       ├── __init__.py         # Package initialization
│       ├── graph.py            # Multi-agent system core
│       ├── prompts.py          # Agent system prompts
│       ├── tools.py            # Trading and research tools
│       ├── database_tools.py   # Data persistence tools
│       ├── state.py            # System state management
│       ├── context.py          # Configuration management
│       └── utils.py            # Utility functions
├── data/                       # Database storage
│   └── trading_orders.db       # SQLite database
├── images/                     # Agent visualizations
│   ├── database_agent.png      # Database agent graph
│   ├── portfolio_agent.png     # Portfolio agent graph
│   ├── research_agent.png      # Research agent graph
│   ├── supervisor_custom.png   # Custom supervisor graph
│   └── supervisor_highlevel.png # High-level supervisor graph
├── publication/                # Academic publication materials
│   ├── NexTrade_Publication.md # Complete publication document
│   ├── Publication_Summary.md  # Executive summary
│   ├── Architecture_Diagrams.md # Technical diagrams
│   ├── Test_Results_September_2025.md # Test validation results
│   └── README.md               # Publication overview
└── tests/                      # Test suite
    ├── conftest.py             # Test configuration
    ├── integration_tests/      # End-to-end tests
    │   ├── __init__.py
    │   └── test_graph.py
    └── unit_tests/             # Component tests
        ├── __init__.py
        └── test_configuration.py
```

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AAIDC-Module2-MultiAgent
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended - fast and modern)
uv venv .venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Install project dependencies using uv
uv sync

# Install LangGraph CLI for advanced features
uv add "langgraph-cli[inmem]"
```

### 4. Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Configure your API keys in the `.env` file:

```env
# Azure OpenAI Configuration (Primary)
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Groq Configuration (Fallback)
GROQ_API_KEY=your_groq_api_key

# Optional: LangSmith Tracing
LANGSMITH_API_KEY=your_langsmith_key
```

### 5. Verify Installation

```bash
python test_agents.py
```

You should see all 8 tests pass, confirming the system is properly configured.

## Usage

### Command Line Interface

#### Run the Test Suite
```bash
# Full automated test suite
python test_agents.py

# Database-specific tests
python test_database_agent.py
```

#### Interactive Trading Session
```bash
python test_agents.py
# Select option 2 for interactive mode
```

### Web Interface

Launch the Streamlit application for a user-friendly interface:

```bash
streamlit run streamlit_app.py
```

The web interface provides:
- Interactive chat with the multi-agent system
- Agent visualization capabilities
- Configuration options for different AI models
- Sample trading scenarios


## Multi-Agent Workflow

### System Architecture

The NexTrade system implements a sophisticated multi-agent architecture with intelligent routing and coordination:

```
User Request
     ↓
┌─────────────────┐
│ SUPERVISOR      │ ──► Analyzes request and routes to appropriate agent
│ AGENT           │
└─────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│           Intelligent Routing               │
│                                             │
│ Research Needed? ──► RESEARCH AGENT         │
│ Trading Required? ──► PORTFOLIO AGENT       │
│ Data Operations? ──► DATABASE AGENT         │
└─────────────────────────────────────────────┘
```

The system provides both high-level and custom supervisor implementations, as shown in the architectural diagrams above. The custom supervisor (Figure 1) offers more granular control over agent coordination, while the high-level supervisor (Figure 5) leverages LangGraph's built-in coordination features for streamlined workflows.

### Agent Specifications

#### 🔍 Research Agent
- **Purpose**: Investment research and market analysis
- **Tools**: Web search, Wikipedia search, market data APIs
- **Capabilities**: Company analysis, market trends, investment recommendations
- **Output**: Factual research with verified information and specific stock recommendations

![Research Agent Graph](images/research_agent.png)

*Figure 2: Research Agent workflow showing web search and analysis capabilities*

#### 📈 Portfolio Agent
- **Purpose**: Trading operations and portfolio management
- **Tools**: Stock lookup, market data, order placement, position tracking
- **Capabilities**: Real-time analysis, trade execution, risk assessment
- **Safety**: Human-in-the-loop approval required for all trades

![Portfolio Agent Graph](images/portfolio_agent.png)

*Figure 3: Portfolio Agent workflow with human-in-the-loop safety mechanisms for trading operations*

#### 💾 Database Agent
- **Purpose**: Data persistence and portfolio tracking
- **Tools**: SQLite operations, order management, historical analytics
- **Capabilities**: Complete audit trails, portfolio calculations, reporting
- **Features**: ACID compliance, user isolation, data integrity

![Database Agent Graph](images/database_agent.png)

*Figure 4: Database Agent workflow managing persistent data storage and retrieval operations*

#### 🎯 Supervisor Agent
- **Purpose**: Workflow orchestration and coordination
- **Tools**: Agent handoff mechanisms, task routing, state management
- **Capabilities**: Intelligent delegation, error handling, workflow completion
- **Features**: Context preservation, multi-step coordination

![Supervisor High-Level Graph](images/supervisor_highlevel.png)

*Figure 5: High-level supervisor implementation using LangGraph's built-in coordination features*

### Workflow Examples

#### Simple Research Workflow
1. User requests investment research
2. Supervisor delegates to Research Agent
3. Research Agent conducts market analysis using web search
4. Results returned with specific company recommendation

#### Complete Trading Workflow
1. User requests trade execution
2. Supervisor delegates to Portfolio Agent
3. Portfolio Agent fetches current market data
4. **Human approval requested** (safety mechanism)
5. Upon approval, trade executed
6. Supervisor delegates to Database Agent
7. Trade details stored with complete audit trail

#### Portfolio Analysis Workflow
1. User requests portfolio summary
2. Supervisor delegates to Database Agent
3. Database Agent retrieves positions and history
4. Comprehensive report generated with analytics

## Data Requirements

### Database Schema

The system uses SQLite with three main tables:

- **orders**: Order tracking with status management
- **portfolio_positions**: Current holdings and valuations
- **trade_history**: Complete transaction history

Database is automatically initialized at: `data/trading_orders.db`

### Expected Data Formats

- **Stock Symbols**: Standard ticker symbols (e.g., AAPL, NVDA, MSFT)
- **Prices**: Decimal values in USD
- **Timestamps**: ISO format with timezone information
- **User IDs**: String identifiers for user isolation

## Testing

### Automated Test Suite

The project includes comprehensive testing covering:

```bash
# Run all tests
python test_agents.py

# Results: 8/8 tests should pass
# - System Initialization
# - Research Agent Functionality
# - Portfolio Agent Operations
# - Database Operations
# - Human-in-the-Loop Safety
# - Complete Trading Workflows
```

### Manual Testing

```bash
# Interactive testing mode
python test_agents.py
# Select option 2 for manual testing

# Database-specific testing
python test_database_agent.py
```

### Expected Test Results

All tests should pass with the following confirmations:
- ✅ Multi-model support (Azure OpenAI + Groq)
- ✅ Agent coordination and handoffs
- ✅ Real-time market data retrieval
- ✅ Human approval mechanisms
- ✅ Database operations and data integrity
- ✅ Complete workflow execution

## Configuration

### Model Configuration

The system supports multiple AI providers with automatic fallback:

```python
# Azure OpenAI (recommended for production)
use_azure = True

# Groq (cost-effective alternative)
use_azure = False
```

### Agent Configuration

Customize agent behavior through system prompts in `src/agent/prompts.py`:

- Research Agent: Modify research depth and sources
- Portfolio Agent: Adjust risk parameters and approval thresholds
- Database Agent: Configure data retention and analytics

### Safety Configuration

Human-in-the-loop settings in `src/agent/tools.py`:

- Approval timeout settings
- Risk threshold configuration
- Notification preferences

## Troubleshooting

### Common Issues

#### API Key Configuration
```bash
# Verify environment variables
python -c "import os; print('Azure:', bool(os.getenv('AZURE_OPENAI_API_KEY'))); print('Groq:', bool(os.getenv('GROQ_API_KEY')))"
```

#### Database Issues
```bash
# Check database status
python -c "from src.agent.database_tools import get_database_stats; print(get_database_stats())"
```

#### Model Connection Issues
- Verify API keys are valid and have sufficient credits
- Check internet connectivity
- Ensure firewall allows outbound HTTPS connections

### Performance Optimization

- Use Azure OpenAI for better tool calling performance
- Enable LangSmith tracing for debugging
- Monitor database size for large portfolios
- Consider rate limiting for high-frequency usage

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `uv sync --dev`
4. Run tests before submitting: `python test_agents.py`
5. Submit pull request with test coverage

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for all public methods
- Maintain test coverage above 90%
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this project in academic work, please cite:

```bibtex
@software{nextrade2025,
  title={NexTrade: Multi-Agent Trading System for Intelligent Stock Market Operations},
  author={AAIDC Module 2 Team},
  year={2025},
  url={https://github.com/your-repo/nextrade}
}
```

## Support

- **Documentation**: See `publication/` directory for detailed technical documentation
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for usage questions
- **Email**: Contact maintainers for enterprise inquiries

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain)
- Inspired by modern multi-agent system research
- Thanks to the open-source AI community for foundational tools

