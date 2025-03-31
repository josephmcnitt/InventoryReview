#!/usr/bin/env python3
"""
Inventory Files Comparer

This module compares inventory data between the official stock tracker spreadsheet
and the downloaded Vagaro inventory file to identify discrepancies.
"""

import os
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventoryComparer:
    """
    Compares inventory data between official stock tracker and Vagaro inventory.
    Identifies discrepancies and generates reports.
    """
    
    def __init__(self, vagaro_file="src/Inventory.xlsx", stock_tracker_file=None):
        """
        Initialize the comparer with file paths.
        
        Args:
            vagaro_file (str): Path to the downloaded Vagaro inventory file
            stock_tracker_file (str): Path to the official stock tracker file
        """
        self.vagaro_file = Path(vagaro_file)
        
        # If stock tracker file not provided, try to find the most recent one
        if stock_tracker_file is None:
            stock_files = list(Path().glob("src/Official Stock Tracker*.xls*"))  # Match both xlsx and xlsb
            if not stock_files:
                raise FileNotFoundError("No Official Stock Tracker file found")
            self.stock_tracker_file = max(stock_files, key=lambda x: x.stat().st_mtime)
        else:
            self.stock_tracker_file = Path(stock_tracker_file)
            
        # Ensure both files exist
        if not self.vagaro_file.exists():
            raise FileNotFoundError(f"Vagaro inventory file not found: {self.vagaro_file}")
        if not self.stock_tracker_file.exists():
            raise FileNotFoundError(f"Stock tracker file not found: {self.stock_tracker_file}")
            
        logger.info(f"Using Vagaro file: {self.vagaro_file}")
        logger.info(f"Using Stock Tracker file: {self.stock_tracker_file}")
        
    def load_data(self):
        """
        Load data from both files into pandas DataFrames.
        Standardizes column names and data types for comparison.
        """
        try:
            # Load Vagaro inventory data (source of truth)
            if self.vagaro_file.suffix.lower() == '.csv':
                self.vagaro_df = pd.read_csv(self.vagaro_file)
            else:
                self.vagaro_df = pd.read_excel(
                    self.vagaro_file,
                    skiprows=2,  # Skip empty rows
                    header=0,    # Use first non-skipped row as header
                    engine='openpyxl'
                )
            print("\nVagaro file columns:", self.vagaro_df.columns.tolist())
            print("\nVagaro first 5 rows:")
            print(self.vagaro_df.head())
            
            # Map Vagaro columns
            vagaro_mapping = {
                'Product': 'item_name',
                'Quantity': 'quantity',
                'Product Category': 'category'
            }
            
            # Create a clean Vagaro DataFrame with only the needed columns
            self.vagaro_df = self.vagaro_df[list(vagaro_mapping.keys())].copy()
            self.vagaro_df.columns = list(vagaro_mapping.values())
            
            # Load official stock tracker data
            if self.stock_tracker_file.suffix.lower() == '.csv':
                self.stock_df = pd.read_csv(self.stock_tracker_file)
            elif self.stock_tracker_file.suffix.lower() == '.xlsb':
                self.stock_df = pd.read_excel(
                    self.stock_tracker_file,
                    engine='pyxlsb',
                    sheet_name=0
                )
            else:
                self.stock_df = pd.read_excel(
                    self.stock_tracker_file,
                    engine='openpyxl'
                )
                
            print("\nStock Tracker columns:", self.stock_df.columns.tolist())
            print("\nStock Tracker first 5 rows:")
            print(self.stock_df.head())
            
            # Map Stock Tracker columns
            stock_mapping = {
                'Product Name': 'item_name',
                'Quantity in Stock': 'quantity',
                'Location of Stock': 'category'  # Using location as category
            }
            
            # Create a clean Stock Tracker DataFrame with only the needed columns
            self.stock_df = self.stock_df[list(stock_mapping.keys())].copy()
            self.stock_df.columns = list(stock_mapping.values())
            
            # Convert quantities to numeric, replacing any non-numeric values with 0
            self.vagaro_df['quantity'] = pd.to_numeric(self.vagaro_df['quantity'], errors='coerce').fillna(0)
            self.stock_df['quantity'] = pd.to_numeric(self.stock_df['quantity'], errors='coerce').fillna(0)
            
            print("\nProcessed data preview:")
            print("\nVagaro data:")
            print(self.vagaro_df.head())
            print("\nStock Tracker data:")
            print(self.stock_df.head())
            
            # Verify data loaded correctly
            if len(self.vagaro_df) == 0:
                raise ValueError("No data loaded from Vagaro file")
            if len(self.stock_df) == 0:
                raise ValueError("No data loaded from Stock Tracker file")
                
            logger.info(f"Loaded {len(self.vagaro_df)} items from Vagaro inventory")
            logger.info(f"Loaded {len(self.stock_df)} items from Stock Tracker")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
            
    def compare_inventory(self):
        """
        Compare inventory levels between the two files.
        
        Returns:
            dict: Dictionary containing comparison results and discrepancies
        """
        try:
            # Merge dataframes on item name to compare quantities
            merged_df = pd.merge(
                self.vagaro_df[['item_name', 'quantity', 'category']],
                self.stock_df[['item_name', 'quantity', 'category']],
                on='item_name',
                how='outer',
                suffixes=('_vagaro', '_reported')
            )
            
            # Fill NaN values with 0 for comparison
            merged_df = merged_df.fillna(0)
            
            # Calculate discrepancies
            merged_df['difference'] = merged_df['quantity_vagaro'] - merged_df['quantity_reported']
            
            # Identify various types of discrepancies
            discrepancies = {
                'missing_in_stock_tracker': merged_df[merged_df['quantity_reported'] == 0]['item_name'].tolist(),
                'missing_in_vagaro': merged_df[merged_df['quantity_vagaro'] == 0]['item_name'].tolist(),
                'quantity_mismatch': merged_df[
                    (merged_df['difference'] != 0) & 
                    (merged_df['quantity_vagaro'] != 0) & 
                    (merged_df['quantity_reported'] != 0)
                ].to_dict('records')
            }
            
            # Generate summary statistics
            summary = {
                'total_items_vagaro': len(self.vagaro_df),
                'total_items_reported': len(self.stock_df),
                'items_missing_in_stock_tracker': len(discrepancies['missing_in_stock_tracker']),
                'items_missing_in_vagaro': len(discrepancies['missing_in_vagaro']),
                'items_with_quantity_mismatch': len(discrepancies['quantity_mismatch']),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'discrepancies': discrepancies,
                'summary': summary,
                'comparison_data': merged_df
            }
            
        except Exception as e:
            logger.error(f"Error comparing inventory: {e}")
            raise
            
    def generate_report(self, comparison_results, output_file=None):
        """
        Generate a detailed report of the comparison results.
        
        Args:
            comparison_results (dict): Results from compare_inventory()
            output_file (str, optional): Path to save the report Excel file
        """
        try:
            # Create report filename if not provided
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"inventory_comparison_report_{timestamp}.xlsx"
                
            # Create Excel writer object
            with pd.ExcelWriter(output_file) as writer:
                # Write summary sheet
                summary_df = pd.DataFrame([comparison_results['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Write discrepancies sheets
                missing_stock_df = pd.DataFrame(comparison_results['discrepancies']['missing_in_stock_tracker'], 
                                             columns=['item_name'])
                missing_stock_df.to_excel(writer, sheet_name='Missing in Stock Tracker', index=False)
                
                missing_vagaro_df = pd.DataFrame(comparison_results['discrepancies']['missing_in_vagaro'], 
                                              columns=['item_name'])
                missing_vagaro_df.to_excel(writer, sheet_name='Missing in Vagaro', index=False)
                
                # Write quantity mismatches
                mismatch_df = pd.DataFrame(comparison_results['discrepancies']['quantity_mismatch'])
                mismatch_df.to_excel(writer, sheet_name='Quantity Mismatches', index=False)
                
                # Write full comparison data
                comparison_results['comparison_data'].to_excel(writer, sheet_name='Full Comparison', index=False)
                
                # Get low stock analysis
                expiration_analysis = self.meds_expiring()
                
                # Create detailed low stock analysis
                if not expiration_analysis['low_stock'].empty:
                    # Load full stock data to get all relevant columns
                    if self.stock_tracker_file.suffix.lower() == '.xlsb':
                        full_stock_df = pd.read_excel(
                            self.stock_tracker_file,
                            engine='pyxlsb',
                            sheet_name=0
                        )
                    else:
                        full_stock_df = pd.read_excel(self.stock_tracker_file)
                    
                    # Get low stock items with all their details
                    low_stock_details = full_stock_df[
                        full_stock_df['Product Name'].isin(expiration_analysis['low_stock']['Product Name'])
                    ].copy()
                    
                    # Add days until expiration
                    low_stock_details['Expiration '] = pd.to_datetime(low_stock_details['Expiration '], errors='coerce')
                    today = pd.Timestamp.now()
                    low_stock_details['Days Until Expiration'] = (low_stock_details['Expiration '] - today).dt.days
                    
                    # Sort by quantity and days until expiration
                    low_stock_details = low_stock_details.sort_values(['Quantity in Stock', 'Days Until Expiration'])
                    
                    # Write low stock analysis
                    low_stock_details.to_excel(writer, sheet_name='Low Stock Analysis', index=False)
                
            logger.info(f"Report generated: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise

    def analyze_quantity_discrepancies(self, comparison_results):
        """
        Analyze quantity discrepancies in detail.
        
        Args:
            comparison_results (dict): Results from compare_inventory()
            
        Returns:
            dict: Detailed analysis of quantity discrepancies
        """
        try:
            merged_df = comparison_results['comparison_data']
            
            # Calculate total value of discrepancies
            merged_df['discrepancy_value'] = merged_df['difference'].abs()
            
            # Group by category to see where discrepancies are most common
            category_analysis = merged_df.groupby('category_vagaro')['discrepancy_value'].agg([
                'count', 'sum', 'mean'
            ]).round(2)
            
            # Identify items with significant discrepancies (>10 units)
            significant_discrepancies = merged_df[
                merged_df['discrepancy_value'] > 10
            ].sort_values('discrepancy_value', ascending=False)
            
            # Calculate percentage of items with discrepancies by category
            category_percentages = merged_df.groupby('category_vagaro').apply(
                lambda x: (x['discrepancy_value'] > 0).mean() * 100
            ).round(2)
            
            return {
                'category_analysis': category_analysis,
                'significant_discrepancies': significant_discrepancies,
                'category_percentages': category_percentages,
                'total_discrepancy_value': merged_df['discrepancy_value'].sum()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing quantity discrepancies: {e}")
            raise
            
    def meds_expiring(self):
        """
        Analyze medication inventory for expiration risks and usage patterns.
        
        Returns:
            dict: Analysis of medication inventory and expiration risks
        """
        try:
            # Load stock tracker data with expiration dates
            if self.stock_tracker_file.suffix.lower() == '.csv':
                stock_df = pd.read_csv(self.stock_tracker_file)
            elif self.stock_tracker_file.suffix.lower() == '.xlsb':
                stock_df = pd.read_excel(
                    self.stock_tracker_file,
                    engine='pyxlsb',
                    sheet_name=0
                )
            else:
                stock_df = pd.read_excel(
                    self.stock_tracker_file,
                    engine='openpyxl'
                )
            
            # Convert expiration date to datetime
            stock_df['Expiration'] = pd.to_datetime(stock_df['Expiration'], errors='coerce')
            
            # Calculate days until expiration
            today = pd.Timestamp.now()
            stock_df['Days Until Expiration'] = (stock_df['Expiration'] - today).dt.days
            
            # Identify medications at risk of expiring (within 30 days)
            expiring_soon = stock_df[
                (stock_df['Days Until Expiration'] <= 30) & 
                (stock_df['Days Until Expiration'] > 0)
            ].sort_values('Days Until Expiration')
            
            # Calculate usage rate (assuming we have historical data)
            # For now, we'll just identify low stock items
            low_stock = stock_df[
                stock_df['Quantity in Stock'] < 10
            ].sort_values('Quantity in Stock')
            
            # Group by location to see distribution of expiring items
            location_analysis = expiring_soon.groupby('Location of Stock').size()
            
            return {
                'expiring_soon': expiring_soon,
                'low_stock': low_stock,
                'location_analysis': location_analysis,
                'total_expiring_soon': len(expiring_soon),
                'total_low_stock': len(low_stock)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing medication expiration: {e}")
            return {
                'expiring_soon': pd.DataFrame(),
                'low_stock': pd.DataFrame(),
                'location_analysis': pd.Series(),
                'total_expiring_soon': 0,
                'total_low_stock': 0
            }

def main():
    """
    Main execution function for inventory comparison.
    """
    try:
        # Initialize comparer
        comparer = InventoryComparer()
        
        # Load data from both files
        comparer.load_data()
        
        # Compare inventory
        results = comparer.compare_inventory()
        
        # Analyze quantity discrepancies
        discrepancy_analysis = comparer.analyze_quantity_discrepancies(results)
        
        # Analyze medication expiration
        expiration_analysis = comparer.meds_expiring()
        
        # Generate report
        report_file = comparer.generate_report(results)
        
        # Print summary to console
        print("\nInventory Comparison Summary:")
        print("-" * 30)
        for key, value in results['summary'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
            
        print("\nQuantity Discrepancy Analysis:")
        print("-" * 30)
        print(f"Total Value of Discrepancies: {discrepancy_analysis['total_discrepancy_value']:.2f}")
        print("\nCategory Analysis:")
        print(discrepancy_analysis['category_analysis'])
        
        print("\nMedication Expiration Analysis:")
        print("-" * 30)
        print(f"Items Expiring Soon (within 30 days): {expiration_analysis['total_expiring_soon']}")
        print(f"Items with Low Stock (<10 units): {expiration_analysis['total_low_stock']}")
        print("\nExpiring Items by Location:")
        print(expiration_analysis['location_analysis'])
        
        print(f"\nDetailed report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise

if __name__ == "__main__":
    main() 