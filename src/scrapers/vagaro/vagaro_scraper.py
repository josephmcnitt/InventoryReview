#!/usr/bin/env python3
"""
Vagaro customer scraper module.
Handles scraping of customer data from the Vagaro business management system.
This module provides functionality to automate interactions with the Vagaro platform,
including login, customer search, and data extraction.
"""

import os
import logging
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configure logging to track the scraper's activities
logger = logging.getLogger(__name__)

class VagaroScraper:
    """
    Scraper for the Vagaro business management system.
    
    This class provides methods to interact with the Vagaro web interface,
    including authentication, customer search, and data extraction.
    It uses Playwright for browser automation and handles various edge cases
    that may occur during the scraping process.
    """
    
    def __init__(self):
        """
        Initialize the scraper with necessary configurations.
        
        Sets up the browser environment, loads credentials from environment variables,
        and prepares directories for storing screenshots during the scraping process.
        """
        self.browser = None
        self.page = None
        self.is_logged_in = False
        
        # Load environment variables from .env file for secure credential management
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded environment variables from .env file")
        
        # Get credentials from environment variables to avoid hardcoding sensitive information
        self.username = os.getenv('VAGARO_USERNAME')
        self.password = os.getenv('VAGARO_PASSWORD')
        
        # Validate that credentials are available before proceeding
        if not self.username or not self.password:
            raise ValueError("Vagaro credentials not found in environment variables")
            
        # Create screenshots directory for debugging and audit purposes
        self.screenshots_dir = Path(__file__).parent / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the browser session
        self._start_browser()
        
    def _start_browser(self):
        """
        Provide manual steps for navigation since we're using an existing browser session.
        """
        logger.info("Manual steps required:")
        print("\nPlease follow these steps in your Chrome browser:")
        print("1. Navigate to: https://us03.vagaro.com/merchants/reports/dashboard")
        print("2. Click on the Settings button (8th item in the top menu)")
        print("3. In the search bar that appears, type 'inventory' and press Enter")
        print("4. Click on the 'Management' button that appears")
        print("5. Once the inventory page loads, press Enter in this terminal to continue...")
        input("\nPress Enter after completing these steps...")
        
    def _take_screenshot(self, name):
        """
        Take a screenshot of the current page state and save it with timestamp.
        
        Args:
            name (str): Base name for the screenshot file
            
        Returns:
            str: Path to the saved screenshot file, or None if failed
        """
        try:
            # Add timestamp to filename to ensure uniqueness and chronological ordering
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            self.page.screenshot(path=str(filepath))
            logger.info(f"Screenshot saved: {filename}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
            
    def _login(self):
        """
        Skip login check since we're using manual navigation.
        """
        self.is_logged_in = True
        return True

    def search_by_phone(self, phone_number):
        """
        Search for a customer by phone number in the Vagaro system.
        
        Navigates to the customer management page, performs a search using the provided
        phone number, and extracts customer information from the results.
        
        Args:
            phone_number (str): The phone number to search for
            
        Returns:
            dict or list: Customer information if found (single dict for one customer,
                         list of dicts for multiple matches), or None if no matches
        """
        try:
            # Ensure logged in before attempting search
            if not self.is_logged_in:
                self._login()
                
            # Format phone number by removing non-numeric characters for consistent searching
            formatted_phone = ''.join(filter(str.isdigit, phone_number))
            logger.info(f"Searching for phone number: {formatted_phone}")
            
            # Navigate to customer search page
            self.page.goto("https://www.vagaro.com/users/customer-management.aspx")
            self._take_screenshot("before_search")
            
            # Wait for the search form to be visible before proceeding
            self.page.wait_for_selector("#txtSearch", state="visible")
            
            # Clear existing search text and fill in search form with formatted phone number
            self.page.click("#txtSearch", click_count=3)  # Triple click to select all existing text
            self.page.fill("#txtSearch", formatted_phone)
            
            # Click search button to initiate the search
            self.page.click("#btnSearch")
            
            # Wait for results to load before processing
            time.sleep(2)  # Give time for search to complete and results to render
            self._take_screenshot("search_results")
            
            # Check if no customers were found
            if self.page.query_selector(".no-results-message"):
                logger.info(f"No customer found for {formatted_phone}")
                return None
                
            # Check if we have multiple results matching the search criteria
            customer_rows = self.page.query_selector_all(".customer-row")
            if len(customer_rows) > 1:
                logger.info(f"Found {len(customer_rows)} customers for {formatted_phone}")
                # Get basic info for all matching customers
                customers_data = []
                for i, row in enumerate(customer_rows):
                    customer_data = self._extract_basic_customer_data(row)
                    if customer_data:
                        customers_data.append(customer_data)
                return customers_data
                
            # If we have exactly one result, get detailed customer information
            if len(customer_rows) == 1:
                # Click on the customer row to view detailed information
                self.page.click(".customer-row")
                self.page.wait_for_selector(".customer-details", state="visible")
                self._take_screenshot("customer_details")
                
                # Extract detailed customer data from the details page
                customer_data = self._extract_detailed_customer_data()
                logger.info(f"Found customer data for {formatted_phone}")
                return customer_data
                
            logger.info(f"No customer found for {formatted_phone}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching for {phone_number}: {e}")
            self._take_screenshot("search_error")
            raise
            
    def _extract_basic_customer_data(self, row_element):
        """
        Extract basic customer data from a search result row.
        
        Parses the HTML elements in a customer row to extract name, phone, and email.
        
        Args:
            row_element: The Playwright element representing a customer row
            
        Returns:
            dict: Basic customer information including name, phone, and email
        """
        try:
            # Extract customer name from the row
            name_element = row_element.query_selector(".customer-name")
            name = name_element.text_content().strip() if name_element else "Unknown"
            
            # Extract phone number from the row
            phone_element = row_element.query_selector(".customer-phone")
            phone = phone_element.text_content().strip() if phone_element else "Unknown"
            
            # Extract email address from the row
            email_element = row_element.query_selector(".customer-email")
            email = email_element.text_content().strip() if email_element else "Unknown"
            
            # Return structured data dictionary with extracted information
            return {
                "name": name,
                "phone": phone,
                "email": email
            }
        except Exception as e:
            logger.error(f"Error extracting basic customer data: {e}")
            return None
            
    def _extract_detailed_customer_data(self):
        """
        Extract detailed customer data from the customer details page.
        
        Parses the customer details page to extract comprehensive information
        including personal details, appointment history, and service preferences.
        
        Returns:
            dict: Detailed customer information including contact details,
                 appointment history, and service preferences
        """
        try:
            # Extract basic personal information from the details page
            name_element = self.page.query_selector(".customer-name")
            phone_element = self.page.query_selector(".customer-phone")
            email_element = self.page.query_selector(".customer-email")
            address_element = self.page.query_selector(".customer-address")
            last_visit_element = self.page.query_selector(".last-visit-date")
            membership_element = self.page.query_selector(".membership-status")
            
            # Compile basic customer information into a structured dictionary
            customer_data = {
                "name": name_element.text_content().strip() if name_element else "Unknown",
                "phone": phone_element.text_content().strip() if phone_element else "Unknown",
                "email": email_element.text_content().strip() if email_element else "Unknown",
                "address": address_element.text_content().strip() if address_element else "Unknown",
                "last_visit": last_visit_element.text_content().strip() if last_visit_element else "Unknown",
                "membership_status": membership_element.text_content().strip() if membership_element else "Unknown"
            }
            
            # Extract appointment history from the details page
            appointments = []
            appointment_rows = self.page.query_selector_all(".appointment-row")
            for row in appointment_rows:
                # Extract details for each appointment
                date_element = row.query_selector(".appointment-date")
                service_element = row.query_selector(".appointment-service")
                provider_element = row.query_selector(".appointment-provider")
                status_element = row.query_selector(".appointment-status")
                
                # Compile appointment information into a structured dictionary
                appointment = {
                    "date": date_element.text_content().strip() if date_element else "Unknown",
                    "service": service_element.text_content().strip() if service_element else "Unknown",
                    "provider": provider_element.text_content().strip() if provider_element else "Unknown",
                    "status": status_element.text_content().strip() if status_element else "Unknown"
                }
                appointments.append(appointment)
            
            customer_data["appointments"] = appointments
            
            # Extract service preferences
            services = []
            service_rows = self.page.query_selector_all(".service-preference-row")
            for row in service_rows:
                name_element = row.query_selector(".service-name")
                frequency_element = row.query_selector(".service-frequency")
                last_booked_element = row.query_selector(".service-last-booked")
                
                service = {
                    "name": name_element.text_content().strip() if name_element else "Unknown",
                    "frequency": frequency_element.text_content().strip() if frequency_element else "Unknown",
                    "last_booked": last_booked_element.text_content().strip() if last_booked_element else "Unknown"
                }
                services.append(service)
                
            customer_data["service_preferences"] = services
            
            return customer_data
            
        except Exception as e:
            logger.error(f"Error extracting detailed customer data: {e}")
            # Fallback to basic info if detailed extraction fails
            name_element = self.page.query_selector(".customer-name")
            phone_element = self.page.query_selector(".customer-phone")
            email_element = self.page.query_selector(".customer-email")
            
            return {
                "name": name_element.text_content().strip() if name_element else "Unknown",
                "phone": phone_element.text_content().strip() if phone_element else "Unknown",
                "email": email_element.text_content().strip() if email_element else "Unknown",
                "error": f"Failed to extract detailed data: {str(e)}"
            }
            
    def close(self):
        """Close the browser."""
        if self.browser:
            self.browser.close()
            logger.info("Browser closed")
            
    def navigate_to_inventory_management(self):
        """
        Skip automated navigation since we're doing it manually.
        """
        return True

    def scrape_inventory_data(self):
        """
        Since we're using manual steps, just provide instructions for downloading.
        """
        print("\nPlease follow these final steps:")
        print("1. Click the download button in the inventory management page")
        print("2. Save the Excel file to your desired location")
        print("3. Press Enter in this terminal when the download is complete...")
        input("\nPress Enter after the file is downloaded...")
        return {"status": "manual_download_completed"}

def main():
    """
    Main execution function for the manual Vagaro data collection process.
    """
    scraper = VagaroScraper()
    try:
        # Guide user through manual navigation and download
        scraper.navigate_to_inventory_management()
        inventory_data = scraper.scrape_inventory_data()
        if inventory_data and inventory_data["status"] == "manual_download_completed":
            logger.info("Manual download process completed successfully")
        
    except Exception as e:
        logger.error(f"Process failed: {e}")
    finally:
        print("\nProcess complete. You can close this terminal window.")

if __name__ == "__main__":
    main() 