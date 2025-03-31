#!/usr/bin/env python3
"""
Test script for the Vagaro scraper.
This script helps test the scraper functionality and capture screenshots.
"""

import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from vagaro_scraper import VagaroScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default test phone number
DEFAULT_PHONE = "3217491497"  # Replace with a real test number

def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment variables from .env file")
    else:
        logger.error(".env file not found")
        raise FileNotFoundError(".env file not found")

def test_login():
    """Test the login functionality."""
    logger.info("Testing login functionality")
    
    try:
        scraper = VagaroScraper()
        logger.info("Login test successful")
        return scraper
    except Exception as e:
        logger.error(f"Login test failed: {e}")
        return None

def test_search(scraper, phone_number):
    """Test the search functionality."""
    logger.info(f"Testing search with phone number: {phone_number}")
    
    try:
        result = scraper.search_by_phone(phone_number)
        if result:
            logger.info(f"Search successful. Found customer data")
            # Pretty print the result
            print(json.dumps(result, indent=2))
        else:
            logger.info("No customer found")
        return result
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        return None

def list_screenshots():
    """List all captured screenshots."""
    screenshots_dir = Path(__file__).parent / "screenshots"
    logger.info("\nCaptured screenshots:")
    
    screenshots = list(screenshots_dir.glob("*.png"))
    if not screenshots:
        logger.info("No screenshots found")
        return
        
    for screenshot in sorted(screenshots, key=lambda x: x.stat().st_mtime, reverse=True):
        logger.info(f"- {screenshot.name} ({screenshot.stat().st_size / 1024:.1f} KB)")

def main():
    """Main test function."""
    scraper = None
    try:
        # Load environment variables
        load_environment()
        
        # Test login
        scraper = test_login()
        if not scraper:
            logger.error("Login test failed, stopping tests")
            return
            
        # Use default phone number without prompting
        test_phone = DEFAULT_PHONE
        logger.info(f"Using default phone number: {test_phone}")
            
        result = test_search(scraper, test_phone)
        
        # List captured screenshots
        list_screenshots()
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main() 