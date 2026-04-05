"""Tests for git_operations module."""

import pytest
from pathlib import Path
from strava_lib.git_operations import get_activity_file_path


class TestGetActivityFilePath:
    """Tests for get_activity_file_path function."""
    
    def test_basic_path_structure(self, tmp_path):
        """Test basic file path structure YYYY/MM/DD/activity.md."""
        activity = {
            "start_date_local": "2024-03-15T10:30:00",
        }
        
        result = get_activity_file_path(activity, str(tmp_path))
        
        assert result == tmp_path / "2024" / "03" / "15" / "activity.md"
    
    def test_multiple_activities_same_day(self, tmp_path):
        """Test handling multiple activities on the same day."""
        activity = {
            "start_date_local": "2024-03-15T10:30:00",
        }
        
        # Create first activity
        first_path = tmp_path / "2024" / "03" / "15"
        first_path.mkdir(parents=True)
        (first_path / "activity.md").touch()
        
        # Get path for second activity
        result = get_activity_file_path(activity, str(tmp_path))
        
        assert result == first_path / "activity-2.md"
    
    def test_three_activities_same_day(self, tmp_path):
        """Test handling three activities on the same day."""
        activity = {
            "start_date_local": "2024-03-15T10:30:00",
        }
        
        # Create first two activities
        path = tmp_path / "2024" / "03" / "15"
        path.mkdir(parents=True)
        (path / "activity.md").touch()
        (path / "activity-2.md").touch()
        
        # Get path for third activity
        result = get_activity_file_path(activity, str(tmp_path))
        
        assert result == path / "activity-3.md"
