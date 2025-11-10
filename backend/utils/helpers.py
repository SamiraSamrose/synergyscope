# File: backend/utils/helpers.py
# Purpose: Utility helper functions

"""
Helper Utilities
Common utility functions used across the application
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional


def generate_id(prefix: str = "") -> str:
    """Generate unique identifier"""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def hash_string(text: str) -> str:
    """Generate SHA256 hash of string"""
    return hashlib.sha256(text.encode()).hexdigest()


def calculate_win_rate(wins: int, losses: int) -> float:
    """Calculate win rate from wins and losses"""
    total = wins + losses
    return wins / total if total > 0 else 0.0


def format_percentage(value: float) -> str:
    """Format decimal as percentage string"""
    return f"{value * 100:.1f}%"


def get_patch_from_version(version: str) -> str:
    """Extract patch number from full version string"""
    parts = version.split('.')
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else version


def calculate_kda(kills: int, deaths: int, assists: int) -> float:
    """Calculate KDA ratio"""
    if deaths == 0:
        return float(kills + assists)
    return (kills + assists) / deaths


def time_ago(timestamp: datetime) -> str:
    """Convert timestamp to human-readable time ago"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 365:
        return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 > 1 else ''} ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute{'s' if diff.seconds // 60 > 1 else ''} ago"
    else:
        return "just now"


def validate_summoner_name(name: str) -> bool:
    """Validate summoner name format"""
    if not name or len(name) < 3 or len(name) > 16:
        return False
    # Summoner names can contain alphanumeric and spaces
    return all(c.isalnum() or c.isspace() for c in name)


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers with default fallback"""
    return numerator / denominator if denominator != 0 else default
