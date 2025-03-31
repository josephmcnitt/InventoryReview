from inventory.files_comparer import InventoryComparer

# Initialize the comparer with our sample files
comparer = InventoryComparer(
    vagaro_file="src/Inventory.csv",
    stock_tracker_file="src/Official Stock Tracker Sample.csv"
)

# Load and compare the data
comparer.load_data()
results = comparer.compare_inventory()

# Generate the report
comparer.generate_report(results, "inventory_comparison_report.xlsx")

# Print summary
print("\nComparison Summary:")
print(f"Total items in Vagaro: {results['summary']['total_items_vagaro']}")
print(f"Total items in Stock Tracker: {results['summary']['total_items_reported']}")
print(f"Items missing in Stock Tracker: {results['summary']['items_missing_in_stock_tracker']}")
print(f"Items missing in Vagaro: {results['summary']['items_missing_in_vagaro']}")
print(f"Items with quantity mismatches: {results['summary']['items_with_quantity_mismatch']}")
print("\nReport generated: inventory_comparison_report.xlsx") 