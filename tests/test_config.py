"""Tests for config module.

NOTE: load_environment() no longer calls load_dotenv() internally.
Calling code is responsible for loading .env files before calling load_environment().
"""

import pytest
import os
from unittest.mock import patch
from strava_lib.config import load_environment


class TestLoadEnvironment:
    """Tests for load_environment function.
    
    These tests verify that load_environment() correctly validates
    environment variables when they are already loaded into os.environ.
    """
    
    def test_missing_required_vars(self):
        """Test that missing required vars raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required"):
                load_environment()
    
    def test_all_required_vars_present(self):
        """Test successful loading with all required vars present in environment."""
        env_vars = {
            "STRAVA_CLIENT_ID": "test_id",
            "STRAVA_CLIENT_SECRET": "test_secret",
            "STRAVA_REFRESH_TOKEN": "test_token",
            "ACTIVITIES_REPO_PATH": "/tmp/test",
            "GIT_EMAIL": "test@example.com",
            "GIT_NAME": "Test User",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_environment()
            
            assert config["STRAVA_CLIENT_ID"] == "test_id"
            assert config["GIT_EMAIL"] == "test@example.com"
    
    def test_optional_vars_with_defaults(self):
        """Test that optional vars get default values when not in environment."""
        env_vars = {
            "STRAVA_CLIENT_ID": "test_id",
            "STRAVA_CLIENT_SECRET": "test_secret",
            "STRAVA_REFRESH_TOKEN": "test_token",
            "ACTIVITIES_REPO_PATH": "/tmp/test",
            "GIT_EMAIL": "test@example.com",
            "GIT_NAME": "Test User",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_environment()
            
            # Should have defaults
            assert config["IMPORT_START_DATE"] == "2012-01-01"
            assert config["IMPORT_BATCH_SIZE"] == "200"
