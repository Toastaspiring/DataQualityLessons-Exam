import argparse
import sys
from src.profiler import CsvProfiler
from src.cleaner import CsvCleaner

def main():
    parser = argparse.ArgumentParser(description="CSV Profiler and Cleaner")
    parser.add_argument('input_file', help="Path to the input CSV file")
    parser.add_argument('--action', choices=['profile', 'clean', 'both'], default='both', help="Action to perform: profile, clean, or both")
    parser.add_argument('--output', help="Path to the output clean CSV file (required for cleaning)")
    parser.add_argument('--fill-na', choices=['mean', 'median', 'mode', 'drop'], default='mean', help="Strategy to fill missing values")
    
    args = parser.parse_args()
    
    # Profile
    if args.action in ['profile', 'both']:
        print(f"Profiling {args.input_file}...")
        profiler = CsvProfiler(args.input_file)
        if profiler.df is not None:
            print("Profiling data...")
            print(profiler.generate_report()) # This now includes Deep Profiling sections
        else:
            print("Failed to load data for profiling.")
            sys.exit(1)

    # Clean
    if args.action in ['clean', 'both']:
        if not args.output:
            print("Error: --output argument is required for cleaning.")
            sys.exit(1)
            
        print(f"Cleaning {args.input_file}...")
        profiler = CsvProfiler(args.input_file) # Re-load needed if we didn't just profile, or just use same object logic if optimized
        # optimization: just use the dataframe we already loaded if possible, but keep simple for now
        
        if profiler.df is not None:
            cleaner = CsvCleaner(profiler.df)
            
        if profiler.df is not None:
            cleaner = CsvCleaner(profiler.df)
            
            print("Running user-specified cleaning (Aggregation, Outliers, Status Extraction)...")
            
            # This handles duplicates aggregation and all parsing logic
            rows_reduced = cleaner.run_user_specific_cleaning()
            
            print(f"Aggregation complete. Rows reduced by: {rows_reduced}")
            print(f"Final Count: {len(cleaner.df)}")
            
            # Save
            cleaner.save_data(args.output)
            print(f"Cleaned data saved to {args.output}")
        else:
            print("Failed to load data for cleaning.")
            sys.exit(1)

if __name__ == "__main__":
    main()
