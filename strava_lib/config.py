#!/usr/bin/env python3
"""
Configuration management for Strava Historical Import.
"""

import os
from typing import Dict


def load_environment() -> Dict[str, str]:
    """
    Load and validate environment variables.

    NOTE: Callers must load .env file before calling this function:
        from pathlib import Path
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / ".env")

    Returns:
        Dictionary containing all required configuration values

    Raises:
        ValueError: If any required environment variable is missing
    """

    required_vars = [
        "STRAVA_CLIENT_ID",
        "STRAVA_CLIENT_SECRET",
        "STRAVA_REFRESH_TOKEN",
        "ACTIVITIES_REPO_PATH",
        "GIT_EMAIL",
        "GIT_NAME",
    ]

    # Optional vars with defaults
    optional_vars = {
        "IMPORT_START_DATE": "2012-01-01",
        "IMPORT_BATCH_SIZE": "200",
    }

    config = {}
    missing_vars = []

    # Check required
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Add optional with defaults
    for var, default in optional_vars.items():
        config[var] = os.environ.get(var, default)

    return config
