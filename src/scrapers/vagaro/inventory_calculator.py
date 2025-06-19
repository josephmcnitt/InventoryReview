#!/usr/bin/env python3
"""
Inventory Calculator for Vagaro.
Processes inventory and transaction data to calculate expected inventory levels
and compares them with the official stock tracker.
"""

import os
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InventoryCalculator:
    """
    Calculator for processing inventory and transaction data.
    
    This class handles:
    1. Reading inventory and transaction data
    2. Calculating expected inventory based on transactions
    3. Comparing with official stock tracker
    4. Generating reports and expected inventory file
    """
    
    def __init__(self):
        """Initialize the calculator with necessary configurations."""
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def read_inventory_file(self, file_path):
        """
        Read the Vagaro inventory file.
        
        Args:
            file_path (str): Path to the inventory file (CSV)
            
        Returns:
            pd.DataFrame: DataFrame containing inventory data
        """
        try:
            df = pd.read_csv(file_path)
            # Rename columns to standardized names
            df = df.rename(columns={
                'Product': 'product_name',
                'Quantity': 'quantity',
                'Product Category': 'location'
            })
            logger.info(f"Successfully read inventory file: {file_path}")
            logger.info(f"Inventory columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            logger.error(f"Error reading inventory file: {e}")
            raise
            
    def read_transaction_file(self, file_path):
        """
        Read the transaction list file.
        
        Args:
            file_path (str): Path to the transaction Excel file
            
        Returns:
            pd.DataFrame: DataFrame containing transaction data
        """
        try:
            df = pd.read_excel(file_path)
            # Add column mapping here once we know the transaction file structure
            logger.info(f"Successfully read transaction file: {file_path}")
            logger.info(f"Transaction columns: {df.columns.tolist()}")
            # Print first few rows to understand structure
            logger.info("First few transactions:")
            logger.info(df.head())
            return df
        except Exception as e:
            logger.error(f"Error reading transaction file: {e}")
            raise
            
    def read_official_tracker(self, file_path):
        """
        Read the official stock tracker file.
        
        Args:
            file_path (str): Path to the official stock tracker CSV
            
        Returns:
            pd.DataFrame: DataFrame containing official stock data
        """
        try:
            df = pd.read_csv(file_path)
            # Rename columns to standardized names
            df = df.rename(columns={
                'Product Name': 'product_name',
                'Quantity in Stock': 'quantity',
                'Location of Stock': 'location'
            })
            logger.info(f"Successfully read official stock tracker: {file_path}")
            logger.info(f"Official tracker columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            logger.error(f"Error reading official stock tracker: {e}")
            raise
            
    def calculate_expected_inventory(self, inventory_df, transaction_df):
        """
        Calculate expected inventory based on current inventory and transactions.
        
        Args:
            inventory_df (pd.DataFrame): Current inventory data
            transaction_df (pd.DataFrame): Transaction data
            
        Returns:
            pd.DataFrame: Expected inventory after transactions
        """
        try:
            # Create a copy of inventory to avoid modifying the original
            expected_inventory = inventory_df.copy()
            logger.info("Starting inventory calculation...")
            logger.info(f"Initial inventory shape: {expected_inventory.shape}")
            
            # Log transaction processing
            logger.info(f"Processing {len(transaction_df)} transactions")
            
            # Process transactions to update inventory
            for idx, transaction in transaction_df.iterrows():
                # Log each transaction for debugging
                logger.info(f"Processing transaction {idx + 1}")
                logger.info(f"Transaction details: {transaction.to_dict()}")
                
                # Get product name and quantity from transaction
                # Adjust these based on actual transaction file columns
                product_name = transaction.get('Product', '')  # Adjust column name as needed
                quantity = transaction.get('Quantity', 0)  # Adjust column name as needed
                
                if product_name and quantity:
                    # Update inventory for this product
                    mask = expected_inventory['product_name'] == product_name
                    if mask.any():
                        expected_inventory.loc[mask, 'quantity'] -= quantity
                        logger.info(f"Updated quantity for {product_name}: {quantity} units subtracted")
                    else:
                        logger.warning(f"Product not found in inventory: {product_name}")
            
            logger.info("Successfully calculated expected inventory")
            logger.info(f"Final inventory shape: {expected_inventory.shape}")
            return expected_inventory
            
        except Exception as e:
            logger.error(f"Error calculating expected inventory: {e}")
            raise
            
    def compare_with_official_tracker(self, expected_inventory_df, official_tracker_df):
        """
        Compare expected inventory with official stock tracker.
        
        Args:
            expected_inventory_df (pd.DataFrame): Expected inventory data
            official_tracker_df (pd.DataFrame): Official stock tracker data
            
        Returns:
            pd.DataFrame: Comparison results showing discrepancies
        """
        try:
            logger.info("Starting inventory comparison...")
            
            # Merge expected inventory with official tracker
            comparison = pd.merge(
                expected_inventory_df,
                official_tracker_df,
                on='product_name',
                how='outer',
                suffixes=('_expected', '_official')
            )
            
            # Calculate differences
            comparison['quantity_difference'] = (
                comparison['quantity_expected'].fillna(0) - 
                comparison['quantity_official'].fillna(0)
            )
            
            # Add status column
            comparison['status'] = comparison['quantity_difference'].apply(
                lambda x: 'Match' if x == 0 else 'Discrepancy'
            )
            
            # Add location comparison
            comparison['location_match'] = (
                comparison['location_expected'] == 
                comparison['location_official']
            )
            
            logger.info("Successfully compared with official tracker")
            logger.info(f"Comparison results shape: {comparison.shape}")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing with official tracker: {e}")
            raise
            
    def generate_reports(self, expected_inventory_df, comparison_df):
        """
        Generate Excel reports with expected inventory and comparison results.
        
        Args:
            expected_inventory_df (pd.DataFrame): Expected inventory data
            comparison_df (pd.DataFrame): Comparison results
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save expected inventory
            expected_file = self.output_dir / f"Expected_Inventory_{timestamp}.xlsx"
            expected_inventory_df.to_excel(expected_file, index=False)
            logger.info(f"Saved expected inventory to: {expected_file}")
            
            # Save comparison results
            comparison_file = self.output_dir / f"Inventory_Comparison_{timestamp}.xlsx"
            comparison_df.to_excel(comparison_file, index=False)
            logger.info(f"Saved comparison results to: {comparison_file}")
            
            # Print summary
            total_items = len(comparison_df)
            discrepancies = len(comparison_df[comparison_df['status'] == 'Discrepancy'])
            location_mismatches = len(comparison_df[~comparison_df['location_match']])
            
            print("\nSummary Report:")
            print("=" * 50)
            print(f"Total items processed: {total_items}")
            print(f"Items with quantity discrepancies: {discrepancies}")
            print(f"Items with location mismatches: {location_mismatches}")
            print(f"Items matching exactly: {total_items - discrepancies}")
            print("\nDetailed discrepancies:")
            
            # Print detailed discrepancies
            discrepancy_items = comparison_df[comparison_df['status'] == 'Discrepancy']
            for _, item in discrepancy_items.iterrows():
                print(f"\nProduct: {item['product_name']}")
                print(f"Expected quantity: {item['quantity_expected']}")
                print(f"Official quantity: {item['quantity_official']}")
                print(f"Difference: {item['quantity_difference']}")
                if not item['location_match']:
                    print(f"Location mismatch: {item['location_expected']} vs {item['location_official']}")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            raise

def main():
    """Main execution function for inventory calculation process."""
    calculator = InventoryCalculator()
    try:
        # Use actual file paths
        inventory_file = "src/Inventory.csv"
        transaction_file = "src/Transaction List.xlsx"
        official_tracker_file = "src/Official Stock Tracker Sample.csv"
        
        logger.info("Starting inventory calculation process...")
        
        # Read all files
        inventory_df = calculator.read_inventory_file(inventory_file)
        transaction_df = calculator.read_transaction_file(transaction_file)
        official_tracker_df = calculator.read_official_tracker(official_tracker_file)
        
        # Calculate expected inventory
        expected_inventory_df = calculator.calculate_expected_inventory(
            inventory_df,
            transaction_df
        )
        
        # Compare with official tracker
        comparison_df = calculator.compare_with_official_tracker(
            expected_inventory_df,
            official_tracker_df
        )
        
        # Generate reports
        calculator.generate_reports(expected_inventory_df, comparison_df)
        
    except Exception as e:
        logger.error(f"Process failed: {e}")
        logger.exception("Detailed error information:")
    finally:
        print("\nProcess complete. Check the output directory for generated files.")

if __name__ == "__main__":
    main() 