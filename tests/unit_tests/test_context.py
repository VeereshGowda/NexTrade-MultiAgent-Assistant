"""
Unit tests for context configuration module.

Tests configuration management and environment setup.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from agent.context import get_default_config


# ==================== Configuration Tests ====================

@pytest.mark.unit
class TestConfiguration:
    """Test configuration management."""
    
    def test_get_default_config_returns_dict(self):
        """Test that default config returns a dictionary."""
        config = get_default_config()
        
        assert isinstance(config, dict)
    
    def test_get_default_config_has_configurable(self):
        """Test that config has configurable key."""
        config = get_default_config()
        
        assert "configurable" in config
    
    def test_get_default_config_has_thread_id(self):
        """Test that configurable has thread_id."""
        config = get_default_config()
        
        assert "thread_id" in config["configurable"]
    
    def test_get_default_config_has_user_id(self):
        """Test that configurable has user_id."""
        config = get_default_config()
        
        assert "user_id" in config["configurable"]
    
    def test_get_default_config_thread_id_is_string(self):
        """Test that thread_id is a string."""
        config = get_default_config()
        
        assert isinstance(config["configurable"]["thread_id"], str)
    
    def test_get_default_config_user_id_is_string(self):
        """Test that user_id is a string."""
        config = get_default_config()
        
        assert isinstance(config["configurable"]["user_id"], str)
    
    def test_get_default_config_thread_id_not_empty(self):
        """Test that thread_id is not empty."""
        config = get_default_config()
        
        assert len(config["configurable"]["thread_id"]) > 0
    
    def test_get_default_config_user_id_not_empty(self):
        """Test that user_id is not empty."""
        config = get_default_config()
        
        assert len(config["configurable"]["user_id"]) > 0
    
    def test_get_default_config_multiple_calls_different_thread_ids(self):
        """Test that multiple calls generate different thread IDs."""
        config1 = get_default_config()
        config2 = get_default_config()
        
        # Thread IDs should be different (UUIDs)
        assert config1["configurable"]["thread_id"] != config2["configurable"]["thread_id"]
    
    def test_get_default_config_structure(self):
        """Test complete config structure."""
        config = get_default_config()
        
        # Verify structure
        assert isinstance(config, dict)
        assert "configurable" in config
        assert isinstance(config["configurable"], dict)
        assert set(config["configurable"].keys()) >= {"thread_id", "user_id"}
