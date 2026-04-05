#!/usr/bin/env python3
"""
Strava API client for Historical Import.
"""

import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

# Constants
STRAVA_TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
STRAVA_ACTIVITY_URL = "https://www.strava.com/api/v3/activities/{id}"
STRAVA_ACTIVITIES_LIST_URL = "https://www.strava.com/api/v3/athlete/activities"
RATE_LIMIT_15MIN = 100
RATE_LIMIT_DAILY = 1000


def refresh_access_token(
    client_id: str, client_secret: str, refresh_token: str
) -> str:
    """
    Refresh Strava OAuth access token.

    Args:
        client_id: Strava application client ID
        client_secret: Strava application client secret
        refresh_token: Current refresh token

    Returns:
        New access token string

    Raises:
        requests.HTTPError: If the API request fails
        requests.Timeout: If the request times out
    """
    logger.info("Refreshing Strava access token...")

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        response = requests.post(STRAVA_TOKEN_URL, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info("Access token refreshed successfully")
        return data["access_token"]
    except requests.HTTPError as e:
        logger.error(f"Failed to refresh token: {e}")
        raise
    except requests.Timeout:
        logger.error("Request timed out while refreshing token")
        raise


def countdown_wait(seconds: int, reason: str) -> None:
    """
    Wait with countdown timer displayed.
    
    Args:
        seconds: Number of seconds to wait
        reason: Reason for waiting (displayed to user)
    
    Example output:
        ⏳ Waiting for 15-minute limit reset...
        ⏱  14:59 remaining...
    """
    print()
    print(f"⏳ Waiting for {reason}...")
    
    end_time = time.time() + seconds
    
    while time.time() < end_time:
        remaining = int(end_time - time.time())
        minutes = remaining // 60
        secs = remaining % 60
        
        # Overwrite same line
        print(f"   ⏱  {minutes:02d}:{secs:02d} remaining...", end="\r", flush=True)
        time.sleep(1)
    
    print()
    print(f"   ✓ Wait complete! Continuing...")
    print()


def check_rate_limit(response_headers: Dict) -> None:
    """
    Check and handle Strava API rate limits.
    
    Strava provides these headers:
        X-RateLimit-Limit: "200,2000"  # 15min limit, daily limit
        X-RateLimit-Usage: "45,780"     # 15min usage, daily usage
        
    Args:
        response_headers: HTTP response headers from Strava API
    """
    limit_header = response_headers.get("X-RateLimit-Limit", "100,1000")
    usage_header = response_headers.get("X-RateLimit-Usage", "0,0")
    
    # Parse limits
    limit_15min, limit_daily = map(int, limit_header.split(","))
    usage_15min, usage_daily = map(int, usage_header.split(","))
    
    # Calculate percentages
    pct_15min = (usage_15min / limit_15min) * 100
    pct_daily = (usage_daily / limit_daily) * 100
    
    logger.debug(
        f"Rate limit: 15min={usage_15min}/{limit_15min} ({pct_15min:.0f}%), "
        f"daily={usage_daily}/{limit_daily} ({pct_daily:.0f}%)"
    )
    
    # Check 15-minute limit
    if pct_15min >= 90:
        wait_seconds = 15 * 60  # 15 minutes
        logger.warning(
            f"⚠️  15-minute rate limit approaching "
            f"({usage_15min}/{limit_15min})"
        )
        countdown_wait(wait_seconds, "15-minute limit reset")
        
    # Check daily limit
    if pct_daily >= 95:
        # Calculate seconds until midnight UTC
        now = datetime.now(timezone.utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight += timedelta(days=1)
        wait_seconds = int((midnight - now).total_seconds())
        
        logger.warning(
            f"⚠️  Daily rate limit approaching "
            f"({usage_daily}/{limit_daily})"
        )
        countdown_wait(wait_seconds, "daily limit reset (midnight UTC)")


def fetch_all_activities(
    access_token: str, 
    after_timestamp: int,
    per_page: int = 200
) -> List[Dict]:
    """
    Fetch ALL activities from Strava with pagination and rate limit handling.
    
    Args:
        access_token: Valid Strava access token
        after_timestamp: Unix timestamp (activities after this date)
        per_page: Activities per page (max 200, default 200)
        
    Returns:
        List of all activities (detailed data)
    """
    all_activities = []
    page = 1
    
    while True:
        logger.info(f"Fetching page {page} (up to {per_page} activities)...")
        
        params = {
            "after": after_timestamp,
            "per_page": per_page,
            "page": page
        }
        
        try:
            response = requests.get(
                STRAVA_ACTIVITIES_LIST_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=30
            )
            
            # Check rate limit BEFORE processing response
            check_rate_limit(response.headers)
            
            response.raise_for_status()
            activities = response.json()
            
            if not activities:
                logger.info("No more activities found")
                break
                
            all_activities.extend(activities)
            logger.info(
                f"   ✓ Page {page}: {len(activities)} activities "
                f"(total: {len(all_activities)})"
            )
            
            page += 1
            
            # Small delay between requests (be nice to Strava)
            time.sleep(0.5)
            
        except requests.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                logger.warning("Rate limit exceeded (429). Waiting 15 minutes...")
                countdown_wait(15 * 60, "rate limit cooldown")
                # Retry same page
                continue
            else:
                logger.error(f"HTTP error while fetching activities: {e}")
                raise
        except requests.Timeout:
            logger.error("Request timed out while fetching activities")
            raise
    
    return all_activities


def fetch_activity_by_id(access_token: str, activity_id: int) -> Dict:
    """
    Fetch a single activity by ID from Strava API.

    Args:
        access_token: Valid Strava access token
        activity_id: Strava activity ID

    Returns:
        Activity data dictionary

    Raises:
        requests.HTTPError: If the API request fails
        requests.Timeout: If the request times out
    """
    url = STRAVA_ACTIVITY_URL.format(id=activity_id)
    logger.debug(f"Fetching activity {activity_id}...")

    try:
        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10
        )
        response.raise_for_status()
        
        # Check rate limit
        check_rate_limit(response.headers)
        
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"Failed to fetch activity {activity_id}: {e}")
        raise
    except requests.Timeout:
        logger.error("Request timed out while fetching activity")
        raise
