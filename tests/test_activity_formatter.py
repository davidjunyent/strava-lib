"""Tests for activity_formatter module."""

import pytest
from datetime import datetime
from strava_lib.activity_formatter import (
    parse_activity_date,
    format_duration,
    format_pace,
    format_activity_markdown,
)


class TestParseActivityDate:
    """Tests for parse_activity_date function."""
    
    def test_parse_with_z_suffix(self):
        """Test parsing date string with Z suffix."""
        result = parse_activity_date("2024-03-15T10:30:00Z")
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_parse_without_z_suffix(self):
        """Test parsing date string without Z suffix."""
        result = parse_activity_date("2024-03-15T10:30:00")
        assert result.year == 2024
        assert result.hour == 10


class TestFormatDuration:
    """Tests for format_duration function."""
    
    def test_hours_minutes_seconds(self):
        """Test formatting duration with hours."""
        assert format_duration(3661) == "01:01:01"
    
    def test_minutes_seconds_only(self):
        """Test formatting duration without hours."""
        assert format_duration(125) == "02:05"
    
    def test_zero_seconds(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "00:00"


class TestFormatPace:
    """Tests for format_pace function."""
    
    def test_valid_pace(self):
        """Test calculating valid pace."""
        # 5 km in 25 minutes = 5:00 min/km
        pace = format_pace(5000, 1500)
        assert pace == "5:00 min/km"
    
    def test_zero_distance(self):
        """Test with zero distance returns None."""
        assert format_pace(0, 1000) is None
    
    def test_zero_time(self):
        """Test with zero time returns None."""
        assert format_pace(5000, 0) is None


class TestFormatActivityMarkdown:
    """Tests for format_activity_markdown function."""
    
    def test_basic_activity(self):
        """Test formatting basic activity."""
        activity = {
            "name": "Morning Run",
            "sport_type": "Run",
            "id": 12345,
            "start_date_local": "2024-03-15T07:30:00",
            "distance": 5000,
            "moving_time": 1500,
            "total_elevation_gain": 50,
        }
        
        markdown = format_activity_markdown(activity)
        
        assert "# Morning Run" in markdown
        assert "**Type:** Run" in markdown
        assert "**Distance:** 5.00 km" in markdown
        assert "**Duration:** 25:00" in markdown
        assert "**Pace:** 5:00 min/km" in markdown
        assert "**Elevation gain:** 50 m" in markdown
        assert "https://www.strava.com/activities/12345" in markdown
    
    def test_activity_with_description(self):
        """Test formatting activity with description."""
        activity = {
            "name": "Test Run",
            "description": "Great weather today!",
            "sport_type": "Run",
            "start_date_local": "2024-03-15T07:30:00",
            "distance": 1000,
            "moving_time": 300,
            "total_elevation_gain": 5,
        }
        
        markdown = format_activity_markdown(activity)
        
        assert "Great weather today!" in markdown
    
    def test_activity_low_elevation(self):
        """Test that low elevation is not shown."""
        activity = {
            "name": "Flat Run",
            "sport_type": "Run",
            "start_date_local": "2024-03-15T07:30:00",
            "distance": 5000,
            "moving_time": 1500,
            "total_elevation_gain": 5,  # < 10m, shouldn't show
        }
        
        markdown = format_activity_markdown(activity)
        
        assert "Elevation gain" not in markdown
