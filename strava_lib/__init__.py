"""Strava integration library - shared utilities for Strava projects."""

from strava_lib.config import load_environment
from strava_lib.strava_api import (
    refresh_access_token,
    fetch_all_activities,
    fetch_activity_by_id,
)
from strava_lib.git_operations import (
    get_activity_file_path,
    save_activity_file,
    create_commit_with_date,
    validate_repo,
)
from strava_lib.activity_formatter import (
    parse_activity_date,
    format_duration,
    format_pace,
    format_activity_markdown,
)

__version__ = "0.1.0"

__all__ = [
    # Config
    "load_environment",
    # Strava API
    "refresh_access_token",
    "fetch_all_activities",
    "fetch_activity_by_id",
    # Git operations
    "get_activity_file_path",
    "save_activity_file",
    "create_commit_with_date",
    "validate_repo",
    # Activity formatting
    "parse_activity_date",
    "format_duration",
    "format_pace",
    "format_activity_markdown",
]
