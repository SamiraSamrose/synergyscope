# File: backend/utils/__init__.py
# Utilities package initialization

"""
Utilities Package
Configuration, logging, and helper functions
"""

from backend.utils.config import get_settings, Settings
from backend.utils.logger import setup_logger
from backend.utils.helpers import (
    generate_id,
    hash_string,
    calculate_win_rate,
    format_percentage,
    get_patch_from_version,
    calculate_kda,
    time_ago,
    validate_summoner_name
)

__all__ = [
    'get_settings',
    'Settings',
    'setup_logger',
    'generate_id',
    'hash_string',
    'calculate_win_rate',
    'format_percentage',
    'get_patch_from_version',
    'calculate_kda',
    'time_ago',
    'validate_summoner_name'
]
