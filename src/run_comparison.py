from inventory.files_comparer import InventoryComparer
import logging

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the comparer with our sample files
        comparer = InventoryComparer(
            vagaro_file="src/Inventory.xlsx",
            stock_tracker_file="src/Official Stock Tracker Sample.xlsx"
        )
        
        # Load the data
        logger.info("Loading data from files...")
        comparer.load_data()
        
        # Compare inventory
        logger.info("Comparing inventory...")
        results = comparer.compare_inventory()
        
        # Generate report
        logger.info("Generating comparison report...")
        comparer.generate_report(results, "inventory_comparison_report.xlsx")
        
        # Print summary
        logger.info("\nComparison Summary:")
        logger.info(f"Total items in Vagaro: {results['summary']['total_items_vagaro']}")
        logger.info(f"Total items in Stock Tracker: {results['summary']['total_items_reported']}")
        logger.info(f"Items missing in Stock Tracker: {results['summary']['items_missing_in_stock_tracker']}")
        logger.info(f"Items missing in Vagaro: {results['summary']['items_missing_in_vagaro']}")
        logger.info(f"Items with quantity mismatches: {results['summary']['items_with_quantity_mismatch']}")
        
        logger.info("\nReport generated: inventory_comparison_report.xlsx")
        
    except Exception as e:
        logger.error(f"Error during comparison: {e}")
        raise

if __name__ == "__main__":
    main() 