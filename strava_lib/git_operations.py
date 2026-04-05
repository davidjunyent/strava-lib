#!/usr/bin/env python3
"""
Git operations for Strava Historical Import.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict

from strava_lib.activity_formatter import parse_activity_date

logger = logging.getLogger(__name__)


def get_activity_file_path(activity: Dict, repo_path: str) -> Path:
    """
    Determine the file path for the activity markdown file.

    Args:
        activity: Activity data dictionary
        repo_path: Path to the activities repository

    Returns:
        Path object for the activity markdown file
    """
    date = parse_activity_date(activity["start_date_local"])
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    activity_dir = Path(repo_path) / year / month / day
    base_filename = "activity.md"

    # Check if activity.md exists, find next available number
    if not (activity_dir / base_filename).exists():
        return activity_dir / base_filename

    # Find next available number
    counter = 2
    while (activity_dir / f"activity-{counter}.md").exists():
        counter += 1

    return activity_dir / f"activity-{counter}.md"


def save_activity_file(markdown_content: str, file_path: Path, repo_path: str) -> Path:
    """
    Save formatted markdown to activity file.

    Args:
        markdown_content: Formatted markdown content
        file_path: Full path to the activity file
        repo_path: Path to the activities repository

    Returns:
        Relative path from repo root
    """
    # Create parent directories
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    file_path.write_text(markdown_content)

    # Return relative path from repo root
    relative_path = file_path.relative_to(repo_path)
    logger.debug(f"Activity saved to {relative_path}")

    return relative_path


def create_commit_with_date(
    repo_path: str, file_path: Path, activity: Dict, git_name: str, git_email: str
) -> None:
    """
    Create a git commit with the activity's date.

    Args:
        repo_path: Path to the activities repository
        file_path: Relative path to the activity file
        activity: Activity data dictionary
        git_name: Git author name
        git_email: Git author email

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    # Parse activity date
    date = parse_activity_date(activity["start_date_local"])
    date_str = date.isoformat()

    # Build commit message
    activity_type = activity.get("sport_type") or activity.get("type", "Activity")
    distance_km = activity.get("distance", 0) / 1000
    date_formatted = date.strftime("%Y-%m-%d")
    commit_message = f"{activity_type} on {date_formatted}: {distance_km:.2f} km"

    # Git add
    logger.debug(f"Staging {file_path}...")
    subprocess.run(
        ["git", "add", str(file_path)],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )

    # Git commit with custom date
    logger.debug(f"Creating commit with date {date_str}...")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    result = subprocess.run(
        [
            "git",
            "commit",
            "-m",
            commit_message,
            "--author",
            f"{git_name} <{git_email}>",
        ],
        cwd=repo_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    # Get commit hash
    commit_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    logger.debug(f"Commit created: {commit_hash[:8]} - {commit_message}")


def validate_repo(repo_path: str) -> None:
    """
    Validate that the activities repository exists and is a git repo.

    Args:
        repo_path: Path to the activities repository

    Raises:
        ValueError: If repo doesn't exist or isn't a git repository
    """
    repo = Path(repo_path)

    if not repo.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    if not repo.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    git_dir = repo / ".git"
    if not git_dir.exists():
        raise ValueError(f"Not a git repository: {repo_path}")
