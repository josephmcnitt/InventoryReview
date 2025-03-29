#!/usr/bin/env python3
"""
Launch Chrome with remote debugging enabled for testing.
"""

import os
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_chrome_path():
    """Find the Chrome executable path."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

def launch_chrome():
    """Launch Chrome with remote debugging enabled."""
    chrome_path = find_chrome_path()
    if not chrome_path:
        logger.error("Chrome not found in common locations")
        sys.exit(1)
        
    # Create user data directory if it doesn't exist
    user_data_dir = os.path.join(os.path.dirname(__file__), "chrome_debug_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    cmd = [
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.vagaro.com"
    ]
    
    try:
        logger.info("Launching Chrome with remote debugging enabled")
        subprocess.Popen(cmd)
        logger.info("Chrome launched successfully")
        logger.info("\nInstructions:")
        logger.info("1. Log into Vagaro in the new Chrome window")
        logger.info("2. Complete 2-factor authentication if required")
        logger.info("3. Once logged in, run test_post_2fa.py to test the search functionality")
    except Exception as e:
        logger.error(f"Failed to launch Chrome: {e}")
        sys.exit(1)

if __name__ == "__main__":
    launch_chrome() 