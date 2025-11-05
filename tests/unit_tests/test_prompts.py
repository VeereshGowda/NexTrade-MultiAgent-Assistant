"""
Unit tests for prompts module to increase coverage.

Tests prompt templates and system messages.
"""

import pytest
from agent.prompts import (
    RESEARCH_SYSTEM_MESSAGE,
    PORTFOLIO_SYSTEM_MESSAGE,
    DATABASE_AGENT_SYSTEM_MESSAGE,
    SUPERVISOR_SYSTEM_MESSAGE,
    SYSTEM_PROMPT
)


# ==================== Prompt Existence Tests ====================

@pytest.mark.unit
class TestPromptExistence:
    """Test that all required prompts exist."""
    
    def test_research_agent_prompt_exists(self):
        """Test that research agent prompt exists."""
        assert RESEARCH_SYSTEM_MESSAGE is not None
    
    def test_portfolio_agent_prompt_exists(self):
        """Test that portfolio agent prompt exists."""
        assert PORTFOLIO_SYSTEM_MESSAGE is not None
    
    def test_database_agent_prompt_exists(self):
        """Test that database agent prompt exists."""
        assert DATABASE_AGENT_SYSTEM_MESSAGE is not None
    
    def test_supervisor_prompt_exists(self):
        """Test that supervisor prompt exists."""
        assert SUPERVISOR_SYSTEM_MESSAGE is not None
    
    def test_system_prompt_exists(self):
        """Test that system prompt exists."""
        assert SYSTEM_PROMPT is not None


# ==================== Prompt Type Tests ====================

@pytest.mark.unit
class TestPromptTypes:
    """Test prompt types and structure."""
    
    def test_research_agent_prompt_is_string(self):
        """Test that research agent prompt is a string."""
        assert isinstance(RESEARCH_SYSTEM_MESSAGE, str)
    
    def test_portfolio_agent_prompt_is_string(self):
        """Test that portfolio agent prompt is a string."""
        assert isinstance(PORTFOLIO_SYSTEM_MESSAGE, str)
    
    def test_database_agent_prompt_is_string(self):
        """Test that database agent prompt is a string."""
        assert isinstance(DATABASE_AGENT_SYSTEM_MESSAGE, str)
    
    def test_supervisor_prompt_is_string(self):
        """Test that supervisor prompt is a string."""
        assert isinstance(SUPERVISOR_SYSTEM_MESSAGE, str)
    
    def test_system_prompt_is_string(self):
        """Test that system prompt is a string."""
        assert isinstance(SYSTEM_PROMPT, str)


# ==================== Prompt Content Tests ====================

@pytest.mark.unit
class TestPromptContent:
    """Test prompt content and key phrases."""
    
    def test_research_agent_prompt_not_empty(self):
        """Test that research agent prompt is not empty."""
        assert len(RESEARCH_SYSTEM_MESSAGE) > 0
    
    def test_portfolio_agent_prompt_not_empty(self):
        """Test that portfolio agent prompt is not empty."""
        assert len(PORTFOLIO_SYSTEM_MESSAGE) > 0
    
    def test_database_agent_prompt_not_empty(self):
        """Test that database agent prompt is not empty."""
        assert len(DATABASE_AGENT_SYSTEM_MESSAGE) > 0
    
    def test_supervisor_prompt_not_empty(self):
        """Test that supervisor prompt is not empty."""
        assert len(SUPERVISOR_SYSTEM_MESSAGE) > 0
    
    def test_research_prompt_mentions_research(self):
        """Test that research prompt mentions research."""
        assert 'research' in RESEARCH_SYSTEM_MESSAGE.lower() or 'search' in RESEARCH_SYSTEM_MESSAGE.lower()
    
    def test_portfolio_prompt_mentions_trading(self):
        """Test that portfolio prompt mentions trading."""
        assert 'portfolio' in PORTFOLIO_SYSTEM_MESSAGE.lower() or 'trading' in PORTFOLIO_SYSTEM_MESSAGE.lower()
    
    def test_database_prompt_mentions_database(self):
        """Test that database prompt mentions database."""
        assert 'database' in DATABASE_AGENT_SYSTEM_MESSAGE.lower() or 'order' in DATABASE_AGENT_SYSTEM_MESSAGE.lower()
    
    def test_supervisor_prompt_mentions_supervisor(self):
        """Test that supervisor prompt mentions supervisor."""
        assert 'supervisor' in SUPERVISOR_SYSTEM_MESSAGE.lower() or 'coordinate' in SUPERVISOR_SYSTEM_MESSAGE.lower()


# ==================== Prompt Format Tests ====================

@pytest.mark.unit
class TestPromptFormat:
    """Test prompt formatting and structure."""
    
    def test_prompts_are_reasonable_length(self):
        """Test that prompts are reasonably sized."""
        assert 10 < len(RESEARCH_SYSTEM_MESSAGE) < 10000
        assert 10 < len(PORTFOLIO_SYSTEM_MESSAGE) < 10000
        assert 10 < len(DATABASE_AGENT_SYSTEM_MESSAGE) < 10000
        assert 10 < len(SUPERVISOR_SYSTEM_MESSAGE) < 10000
    
    def test_prompts_are_different(self):
        """Test that each prompt is unique."""
        prompts = [
            RESEARCH_SYSTEM_MESSAGE,
            PORTFOLIO_SYSTEM_MESSAGE,
            DATABASE_AGENT_SYSTEM_MESSAGE,
            SUPERVISOR_SYSTEM_MESSAGE
        ]
        # Check all prompts are different
        for i, prompt1 in enumerate(prompts):
            for j, prompt2 in enumerate(prompts):
                if i != j:
                    assert prompt1 != prompt2
