# NexTrade Demo Scripts

This folder contains interactive demo scripts for manually testing and demonstrating the NexTrade Multi-Agent Trading System.

## 📋 Available Demos

### 1. **demo_agents.py** - Complete System Demo
Interactive testing suite for the entire multi-agent system.

**Features:**
- System initialization testing (Azure OpenAI + Groq)
- Research Agent testing
- Portfolio Agent testing
- Database Agent testing
- Order history functionality
- Human-in-the-loop (HITL) approval mechanism
- Full investment scenario workflow
- Interactive mode for custom queries

**Usage:**
```bash
python demos/demo_agents.py
```

**Menu Options:**
1. Run Full Test Suite (8 automated scenarios)
2. Interactive Testing Mode
3. Exit

---

### 2. **demo_database_agent.py** - Database Operations Demo
Tests database tools and Database Agent integration.

**Features:**
- Database statistics
- Order insertion
- Order retrieval
- Portfolio positions
- Database agent queries

**Usage:**
```bash
python demos/demo_database_agent.py
```

---

### 3. **demo_hitl_complete.py** - HITL Mechanism Demo
Demonstrates the corrected Human-in-the-Loop interrupt detection.

**Features:**
- Trading request with HITL approval
- Interrupt detection
- Approval/rejection workflow
- Command resume functionality

**Usage:**
```bash
python demos/demo_hitl_complete.py
```

---

### 4. **demo_place_order_hitl.py** - Order Placement with HITL
Tests the place_order tool with Human-in-the-Loop functionality.

**Features:**
- Mock state creation with tool calls
- Risky tools interception
- Human approval simulation
- Order execution workflow

**Usage:**
```bash
python demos/demo_place_order_hitl.py
```

---

## 🚀 Quick Start

### Run the Main Demo:
```bash
# From project root
python demos/demo_agents.py
```

### Prerequisites:
- Virtual environment activated
- Environment variables configured (`.env` file)
- All dependencies installed (`uv pip install -e .`)

---

## 📝 Note

These are **manual testing tools**, not automated pytest tests. They are designed for:
- ✅ Interactive demonstration of system capabilities
- ✅ Manual validation of agent behavior
- ✅ Human-in-the-loop workflow testing
- ✅ Live system exploration

For **automated testing**, see the `tests/` folder with pytest-based test suites.

---

## 🎯 Typical Workflow

1. **Start with demo_agents.py** for a comprehensive overview
2. **Test specific features** with focused demos (database, HITL)
3. **Use interactive mode** to explore custom scenarios
4. **Verify HITL mechanism** with trading demos

---

## 💡 Tips

- Use **Azure OpenAI** for better performance (when available)
- Test with **small amounts** first (e.g., 10 shares)
- Watch for **🚨 HITL approval prompts** in trading scenarios
- Check **compliance.log** for safety validation records

---

**Last Updated:** November 4, 2025
