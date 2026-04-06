#!/usr/bin/env python3
"""
Activity formatting utilities for Strava Historical Import.
"""

from datetime import datetime
from typing import Dict, Optional


def parse_activity_date(date_str: str) -> datetime:
    """
    Parse ISO 8601 date string to datetime object.

    Args:
        date_str: ISO 8601 formatted date string

    Returns:
        Parsed datetime object
    """
    # Handle both with and without 'Z' suffix
    if date_str.endswith("Z"):
        date_str = date_str[:-1]
    return datetime.fromisoformat(date_str)


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS or MM:SS.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_pace(distance_m: float, moving_time: int) -> Optional[str]:
    """
    Calculate and format pace in min/km.
    
    Args:
        distance_m: Distance in meters
        moving_time: Moving time in seconds
        
    Returns:
        Formatted pace string (e.g., "5:58 min/km") or None if cannot calculate
    """
    if distance_m <= 0 or moving_time <= 0:
        return None
    
    # Calculate pace: seconds per kilometer
    pace_per_km = (moving_time / distance_m) * 1000
    
    minutes = int(pace_per_km // 60)
    seconds = int(pace_per_km % 60)
    
    return f"{minutes}:{seconds:02d} min/km"


def format_activity_markdown(activity: Dict) -> str:
    """
    Format activity data as markdown.

    Args:
        activity: Activity data dictionary

    Returns:
        Formatted markdown string
    """
    # Extract basic fields
    name = activity.get("name", "Untitled Activity")
    description = activity.get("description")
    # Use sport_type for more specific activity types (TrailRun, Run, etc.)
    # Fall back to type if sport_type is not available
    activity_type = activity.get("sport_type") or activity.get("type", "Unknown")
    activity_id = activity.get("id")
    date_str = activity.get("start_date_local", "")
    distance_m = activity.get("distance", 0)
    moving_time = activity.get("moving_time", 0)
    elevation_gain = activity.get("total_elevation_gain", 0)

    # Convert distance to km
    distance_km = distance_m / 1000

    # Format date
    date = parse_activity_date(date_str)
    formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")

    # Format duration
    duration = format_duration(moving_time)
    
    # Calculate pace
    pace = format_pace(distance_m, moving_time)

    # Build markdown
    markdown_parts = []
    
    # Add title
    markdown_parts.append(f"# {name}")
    
    # Add description if present
    if description and description.strip():
        markdown_parts.append("")  # Blank line after title
        markdown_parts.append(description.strip())
    
    # Add blank line before metadata
    markdown_parts.append("")
        
    # Add activity type
    markdown_parts.append(f"**Type:** {activity_type}  ")
    
    # Add activity id    
    markdown_parts.append(f"**Activity ID:** {activity_id}  ")
    
    # Add remaining metadata
    markdown_parts.append(f"**Date:** {formatted_date}  ")
    markdown_parts.append(f"**Distance:** {distance_km:.2f} km  ")
    markdown_parts.append(f"**Duration:** {duration}  ")
    
    # Add pace if available
    if pace:
        markdown_parts.append(f"**Pace:** {pace}  ")
    
    # Add elevation gain if significant (> 10m)
    if elevation_gain > 10:
        markdown_parts.append(f"**Elevation gain:** {elevation_gain:.0f} m  ")
    
    # Add Strava link with activity ID
    if activity_id:
        strava_url = f"https://www.strava.com/activities/{activity_id}"
        gpx_export_url = f"https://www.strava.com/activities/{activity_id}/export_gpx"
        markdown_parts.append(f"**Strava:** [View on Strava]({strava_url})  ")
        markdown_parts.append(f"**GPX:** [Export GPX]({gpx_export_url})  ")
    
    return "\n".join(markdown_parts) + "\n"
