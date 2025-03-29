#!/usr/bin/env python3
"""
Test script for the Vagaro scraper post-2FA authentication.
This script connects to an already open browser where you're logged into Vagaro.
"""

import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime

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

def test_customer_search(phone_number):
    """
    Test customer search functionality using an existing browser instance.
    
    Args:
        phone_number (str): Phone number to search for
    """
    logger.info(f"Testing customer search with phone number: {phone_number}")
    
    try:
        with sync_playwright() as p:
            # Connect to the existing browser instance
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            logger.info("Connected to existing browser")
            
            # Use the first page or create a new one
            pages = browser.contexts[0].pages
            page = pages[0] if pages else browser.contexts[0].new_page()
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = Path(__file__).parent / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            def take_screenshot(name):
                """Take a screenshot and save it with timestamp."""
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{name}_{timestamp}.png"
                    filepath = screenshots_dir / filename
                    page.screenshot(path=str(filepath))
                    logger.info(f"Screenshot saved: {filename}")
                except Exception as e:
                    logger.error(f"Failed to take screenshot: {e}")
            
            # Check if we're on the business selection screen
            current_url = page.url
            logger.info(f"Current URL: {current_url}")
            
            # Navigate directly to business selection
            logger.info("Navigating to business selection page")
            page.goto("https://www.vagaro.com/ShopOwner/ChooseBusiness.aspx")
            page.wait_for_load_state("networkidle")
            
            # Log page content for debugging
            logger.info("Page content:")
            content = page.content()
            logger.info(content[:1000] + "...")  # Log first 1000 chars
            
            # Wait for page to be ready
            logger.info("Waiting for page to be ready...")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_load_state("networkidle")
            
            # Take screenshot of current state
            take_screenshot("business_selection")
            
            # Try different selectors for the business dropdown
            logger.info("Trying different selectors for business dropdown...")
            business_selector = None
            dropdown_selectors = [
                "select[placeholder='Select Business / Shop Owner']",
                "select",
                "#businessSelect",
                ".business-select",
                "[name='business']",
                "[id*='business' i]",
                "[class*='business' i]"
            ]
            
            for selector in dropdown_selectors:
                logger.info(f"Trying selector: {selector}")
                try:
                    business_selector = page.wait_for_selector(selector, state="visible", timeout=5000)
                    if business_selector:
                        logger.info(f"Found business dropdown with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not business_selector:
                # Log all select elements on the page
                selects = page.query_selector_all("select")
                logger.info(f"Found {len(selects)} select elements on page:")
                for select in selects:
                    try:
                        select_info = {
                            "id": select.get_attribute("id"),
                            "class": select.get_attribute("class"),
                            "name": select.get_attribute("name"),
                            "placeholder": select.get_attribute("placeholder")
                        }
                        logger.info(f"Select element: {select_info}")
                    except:
                        pass
                raise Exception("Could not find business selection dropdown")
            
            # Wait a moment for any animations
            page.wait_for_timeout(1000)
            
            # Click to open dropdown
            business_selector.click()
            logger.info("Clicked business selector")
            
            # Wait for dropdown options to be visible
            page.wait_for_timeout(1000)
            
            # Try to find options in different ways
            logger.info("Looking for dropdown options...")
            first_option = None
            option_selectors = [
                "select option:not([value=''])",
                "select option:not(:first-child)",
                ".business-option",
                "[role='option']"
            ]
            
            for selector in option_selectors:
                logger.info(f"Trying option selector: {selector}")
                try:
                    first_option = page.wait_for_selector(selector, state="visible", timeout=5000)
                    if first_option:
                        logger.info(f"Found option with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if first_option:
                first_option.click()
                logger.info("Selected first business option")
                
                # Try different selectors for Apply button
                apply_button = None
                button_selectors = [
                    "button:has-text('Apply')",
                    "[role='button']:has-text('Apply')",
                    ".apply-button",
                    "#applyButton",
                    "input[type='submit']",
                    "button.primary"
                ]
                
                for selector in button_selectors:
                    logger.info(f"Trying button selector: {selector}")
                    try:
                        apply_button = page.wait_for_selector(selector, state="visible", timeout=5000)
                        if apply_button:
                            logger.info(f"Found Apply button with selector: {selector}")
                            break
                    except Exception:
                        continue
                
                if apply_button:
                    apply_button.click()
                    logger.info("Clicked Apply button")
                    # Wait for navigation
                    page.wait_for_load_state("networkidle")
                    logger.info("Navigation completed after business selection")
                else:
                    logger.error("Could not find Apply button")
                    raise Exception("Apply button not found")
            else:
                logger.error("No business options found in dropdown")
                raise Exception("No business options available")
            
            # Navigate to customer management
            logger.info("Navigating to customer management")
            page.goto("https://www.vagaro.com/users/customer-management.aspx")
            # Wait for navigation to complete
            page.wait_for_load_state("networkidle")
            current_url = page.url
            logger.info(f"After navigation, current URL: {current_url}")
            take_screenshot("customer_management")
            
            # Log page content for debugging
            logger.info("Page content:")
            content = page.content()
            logger.info(content[:500] + "...")  # Log first 500 chars
            
            # Check if we need to select business again
            if "choose-business" in current_url.lower():
                logger.info("Redirected to business selection, handling it again")
                business_selector = page.wait_for_selector("select[placeholder='Select Business / Shop Owner']", state="visible", timeout=10000)
                if business_selector:
                    logger.info("Found business selection dropdown")
                    page.wait_for_timeout(1000)
                    business_selector.click()
                    logger.info("Clicked business selector")
                    page.wait_for_timeout(1000)
                    first_option = page.wait_for_selector("select[placeholder='Select Business / Shop Owner'] option:not([value=''])", state="visible")
                    if first_option:
                        first_option.click()
                        logger.info("Selected first business option")
                        apply_button = page.get_by_role("button", name="Apply")
                        if apply_button:
                            apply_button.click()
                            logger.info("Clicked Apply button")
                            page.wait_for_load_state("networkidle")
                            logger.info("Navigation completed after business selection")
                    else:
                        logger.error("No business options found in dropdown")
                        raise Exception("No business options available")
            
            # Format phone number
            formatted_phone = ''.join(filter(str.isdigit, phone_number))
            logger.info(f"Searching for formatted phone: {formatted_phone}")
            
            # Wait for page to be ready
            logger.info("Waiting for page to be ready...")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_load_state("networkidle")
            
            # Try different selectors for search input
            logger.info("Trying different selectors for search input...")
            search_input = None
            selectors = [
                "#txtSearch",
                "input[type='text']",
                "input[placeholder*='search' i]",
                "input[placeholder*='find' i]",
                "input.search-input",
                "[data-testid='search-input']"
            ]
            
            for selector in selectors:
                logger.info(f"Trying selector: {selector}")
                try:
                    search_input = page.wait_for_selector(selector, state="visible", timeout=5000)
                    if search_input:
                        logger.info(f"Found search input with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not search_input:
                # Take screenshot of current state
                take_screenshot("search_input_not_found")
                logger.error("Could not find search input with any selector")
                # Log all input elements on the page
                inputs = page.query_selector_all("input")
                logger.info(f"Found {len(inputs)} input elements on page:")
                for input in inputs:
                    try:
                        input_info = {
                            "id": input.get_attribute("id"),
                            "class": input.get_attribute("class"),
                            "type": input.get_attribute("type"),
                            "placeholder": input.get_attribute("placeholder")
                        }
                        logger.info(f"Input element: {input_info}")
                    except:
                        pass
                raise Exception("Could not find search input")
            
            # Clear existing search text and fill
            search_input.click(click_count=3)  # Triple click to select all
            search_input.fill(formatted_phone)
            logger.info("Filled search input")
            
            # Click search button
            search_button = page.wait_for_selector("#btnSearch")
            if not search_button:
                raise Exception("Could not find search button")
            search_button.click()
            logger.info("Clicked search button")
            
            # Wait for results and take screenshot
            page.wait_for_timeout(2000)  # Wait for results to load
            take_screenshot("search_results")
            
            # Check for results
            no_results = page.query_selector(".no-results-message")
            if no_results:
                logger.info("No results found")
                return None
                
            # Find customer rows
            customer_rows = page.query_selector_all(".customer-row")
            if not customer_rows:
                logger.info("No customer rows found")
                return None
                
            logger.info(f"Found {len(customer_rows)} customer(s)")
            
            # If single result, get detailed info
            if len(customer_rows) == 1:
                customer_rows[0].click()
                page.wait_for_selector(".customer-details", state="visible")
                take_screenshot("customer_details")
                
                # Extract customer details
                details = {}
                for field in ["name", "phone", "email", "address", "last-visit"]:
                    element = page.query_selector(f".customer-{field}")
                    if element:
                        details[field] = element.text_content().strip()
                result = details
            else:
                # Get basic info for all results
                result = []
                for row in customer_rows:
                    customer_data = {}
                    for field in ["name", "phone", "email"]:
                        element = row.query_selector(f".customer-{field}")
                        if element:
                            customer_data[field] = element.text_content().strip()
                    if customer_data:
                        result.append(customer_data)
                    
            # Print results
            print("\nSearch Results:")
            print(json.dumps(result, indent=2))
            return result
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return None

if __name__ == "__main__":
    try:
        load_environment()
        test_customer_search(DEFAULT_PHONE)
    except Exception as e:
        logger.error(f"Test failed: {e}") 