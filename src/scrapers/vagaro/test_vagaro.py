#!/usr/bin/env python3
"""
Test script for the Vagaro scraper.
This script helps test the scraper functionality and capture screenshots.
"""

import os
import logging
from pathlib import Path
from vagaro_scraper import VagaroScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Set up test environment variables."""
    # Check if credentials are already set
    if not os.getenv('VAGARO_USERNAME') or not os.getenv('VAGARO_PASSWORD'):
        logger.info("Please enter your Vagaro credentials:")
        username = input("Username: ")
        password = input("Password: ")
        
        # Set environment variables
        os.environ['VAGARO_USERNAME'] = username
        os.environ['VAGARO_PASSWORD'] = password
        
    logger.info("Environment variables set")

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
            logger.info(f"Search successful. Found customer: {result}")
        else:
            logger.info("No customer found")
        return result
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        return None

def main():
    """Main test function."""
    try:
        # Set up test environment
        setup_test_environment()
        
        # Test login
        scraper = test_login()
        if not scraper:
            logger.error("Login test failed, stopping tests")
            return
            
        # Test search with a known phone number
        test_phone = input("Enter a phone number to search (or press Enter for default test number): ").strip()
        if not test_phone:
            test_phone = "1234567890"
            
        result = test_search(scraper, test_phone)
        
        # List captured screenshots
        screenshots_dir = Path(__file__).parent / "screenshots"
        logger.info("\nCaptured screenshots:")
        for screenshot in screenshots_dir.glob("*.png"):
            logger.info(f"- {screenshot.name}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main() 