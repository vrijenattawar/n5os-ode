"""
Meeting Configuration Module

This module provides centralized configuration for meeting ingestion scripts,
allowing path customization through environment variables for deployment flexibility.

Environment Variables:
    ZO_WORKSPACE (str): Base workspace directory. Default: /home/workspace
        The root directory of the Zo workspace containing all user data.
        
    MEETINGS_DIR (str): Meeting storage directory. Default: {WORKSPACE}/Personal/Meetings
        Where all processed meeting files are permanently stored.
        
    STAGING_DIR (str): Temporary staging directory. Default: {MEETINGS_DIR}/Inbox  
        Where meeting files are temporarily staged before processing.
        
    LOG_DIR (str): Logging directory. Default: {WORKSPACE}/N5/logs
        Where meeting ingestion logs are written.
        
    REGISTRY_DB (str): Meeting registry database. Default: {WORKSPACE}/N5/data/meeting_registry.db
        SQLite database tracking all ingested meetings and their metadata.
        
    TIMEZONE (str): Default timezone for meeting timestamps. Default: UTC
        Timezone used when meeting timestamps lack timezone information.
        
    ENABLE_SMS (str): Enable SMS notifications. Default: false
        Set to "true" to enable SMS notifications for meeting ingestion events.
        Accepts: true, false, 1, 0, yes, no (case insensitive).
"""

import os
from pathlib import Path

# Base workspace directory
WORKSPACE = os.environ.get('ZO_WORKSPACE', '/home/workspace')

# Core meeting directories
MEETINGS_DIR = os.environ.get('MEETINGS_DIR', f'{WORKSPACE}/Personal/Meetings')
STAGING_DIR = os.environ.get('STAGING_DIR', f'{MEETINGS_DIR}/Inbox')

# System directories  
LOG_DIR = os.environ.get('LOG_DIR', f'{WORKSPACE}/N5/logs')
REGISTRY_DB = os.environ.get('REGISTRY_DB', f'{WORKSPACE}/N5/data/meeting_registry.db')

# Configuration settings
TIMEZONE = os.environ.get('TIMEZONE', 'UTC')

# Feature flags
_sms_env = os.environ.get('ENABLE_SMS', 'false').lower()
ENABLE_SMS = _sms_env in ('true', '1', 'yes', 'on')

# Ensure Path objects for directory operations
WORKSPACE_PATH = Path(WORKSPACE)
MEETINGS_PATH = Path(MEETINGS_DIR)
STAGING_PATH = Path(STAGING_DIR)
LOG_PATH = Path(LOG_DIR)
REGISTRY_PATH = Path(REGISTRY_DB)