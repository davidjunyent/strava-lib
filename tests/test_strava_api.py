"""Tests for strava_api module."""

import pytest
from unittest.mock import patch, Mock
from strava_lib.strava_api import refresh_access_token


class TestRefreshAccessToken:
    """Tests for refresh_access_token function."""
    
    @patch('strava_lib.strava_api.requests.post')
    def test_successful_refresh(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "new_token_123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        token = refresh_access_token("client_id", "client_secret", "refresh_token")
        
        assert token == "new_token_123"
        mock_post.assert_called_once()
    
    @patch('strava_lib.strava_api.requests.post')
    def test_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        mock_post.side_effect = Exception("HTTP Error")
        
        with pytest.raises(Exception):
            refresh_access_token("client_id", "client_secret", "refresh_token")
