#!/usr/bin/env python3
"""
Transaction scraper module for Vagaro.
Handles manual navigation and download of transaction data from the Vagaro business management system.
This module provides step-by-step instructions for users to navigate through the Vagaro platform
and download transaction reports.
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionScraper:
    """
    Manual transaction scraper for the Vagaro business management system.
    
    This class provides step-by-step instructions for users to navigate through
    the Vagaro web interface and download transaction reports.
    """
    
    def __init__(self):
        """
        Initialize the scraper with necessary configurations.
        
        Sets up logging and prepares for manual navigation steps.
        """
        # Create screenshots directory for debugging and audit purposes
        self.screenshots_dir = Path(__file__).parent / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    def navigate_to_transactions(self):
        """
        Guide user through navigation to the transaction list page.
        """
        print("\nPlease follow these steps to navigate to the transaction list:")
        print("1. Navigate to: https://us03.vagaro.com/merchants/reports/sales/transactionlist")
        print("2. Once the page loads, press Enter in this terminal to continue...")
        input("\nPress Enter after completing these steps...")
        return True
        
    def set_date_range(self):
        """
        Guide user through setting the date range for transactions.
        """
        # Calculate date range (one week before today)
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        print("\nPlease follow these steps to set the date range:")
        print("1. Click on the date control button (shows current date)")
        print("2. In the 'From' box, enter the date:", week_ago.strftime("%b %d, %Y"))
        print("3. Click the 'Submit' button")
        print("4. Click the 'Run Report' button")
        print("5. Wait for the data to load (this may take a few seconds)")
        print("6. Press Enter in this terminal when the data is loaded...")
        input("\nPress Enter after completing these steps...")
        return True
        
    def download_transactions(self):
        """
        Guide user through downloading the transaction report.
        """
        print("\nPlease follow these steps to download the transaction report:")
        print("1. Click the 'Export' button")
        print("2. Click 'Excel' in the dropdown menu")
        print("3. Save the Excel file to your desired location")
        print("4. Press Enter in this terminal when the download is complete...")
        input("\nPress Enter after completing these steps...")
        return {"status": "manual_download_completed"}

def main():
    """
    Main execution function for the manual transaction data collection process.
    """
    scraper = TransactionScraper()
    try:
        # Guide user through manual navigation and download
        logger.info("Starting transaction data collection process")
        
        # Navigate to transactions page
        if not scraper.navigate_to_transactions():
            logger.error("Failed to navigate to transactions page")
            return
            
        # Set date range and run report
        if not scraper.set_date_range():
            logger.error("Failed to set date range")
            return
            
        # Download the report
        result = scraper.download_transactions()
        if result and result["status"] == "manual_download_completed":
            logger.info("Transaction report download completed successfully")
        
    except Exception as e:
        logger.error(f"Process failed: {e}")
    finally:
        print("\nProcess complete. You can close this terminal window.")

if __name__ == "__main__":
    main() 