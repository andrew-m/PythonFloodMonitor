#!/usr/bin/env python3
# localRun.py - Script to run both local file and URL data fetching and processing

from fetchRiverData import fetch_river_data_from_file, fetch_river_data_from_url, fetch_river_data, REQUESTS_AVAILABLE
from downsampleRiverData import downsample_river_data, write_downsampled_data, scaleValues
import io
import urllib.request


def process_local_file(file_path, output_file_name="output_local.csv"):
    """
    Process data from a local CSV file, downsample it, and write output
    
    Args:
        file_path: Path to the local CSV file
        output_file: Path to write downsampled output
    """
    print(f"\n=== Processing local file: {file_path} ===")
    
    # Fetch data from local file
    with fetch_river_data_from_file(file_path) as stream:
        data_tuples, first_timestamp, last_timestamp = fetch_river_data(stream)
    
    # Downsample the data
    print("\n=== Downsampling local data using LTTB algorithm ===")
    downsampled_heights = downsample_river_data(data_tuples, first_timestamp, last_timestamp)
    
    # Scale the values for display
    print("\n=== Scaling height values to percentages ===")
    highestEverHeight = 1.46  # Constant for highest ever height in meters
    topOfNormalRange = 0.6   # Constant for top of normal range in meters
    topOfGraph, highestEverPerc, normalRangePerc, scaled_heights = scaleValues(highestEverHeight, topOfNormalRange, downsampled_heights)
    
    print(f"Top of graph value: {topOfGraph} meters")
    print(f"Highest ever percentage: {highestEverPerc}%")
    print(f"Normal range percentage: {normalRangePerc}%")
    
    # Write the scaled data to a file
    write_downsampled_data(output_file_name, scaled_heights, first_timestamp, last_timestamp, topOfGraph, highestEverPerc, normalRangePerc)
    
    # Show sample of downsampled data
    print(f"\n=== Sample of downsampled local data (first 10 points) ===")
    for i, height in enumerate(downsampled_heights[:10]):
        print(f"{i+1}: {height}")
    print("...")


def process_url_data(url, output_file_name="output_url.csv"):
    """
    Process data from a URL, downsample it, and write output
    
    Args:
        url: URL of the CSV data
        output_file: Path to write downsampled output
    """
    print(f"\n=== Processing from URL: {url} ===")
    
    try:
        # Try to fetch data using the appropriate method
        if REQUESTS_AVAILABLE:
            print("Using requests module to fetch data...")
            with fetch_river_data_from_url(url) as stream:
                data_tuples, first_timestamp, last_timestamp = fetch_river_data(stream)
        else:
            print("Requests module not available, using urllib instead...")
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                stream = io.StringIO(content)
                data_tuples, first_timestamp, last_timestamp = fetch_river_data(stream)
        
        # Downsample the data
        print("\n=== Downsampling URL data using LTTB algorithm ===")
        downsampled_heights = downsample_river_data(data_tuples, first_timestamp, last_timestamp)
        
        # Scale the values for display
        print("\n=== Scaling height values to percentages ===")
        highestEverHeight = 1.46  # Constant for highest ever height in meters
        topOfNormalRange = 0.6   # Constant for top of normal range in meters
        topOfGraph, highestEverPerc, normalRangePerc, scaled_heights = scaleValues(highestEverHeight, topOfNormalRange, downsampled_heights)
        
        print(f"Top of graph value: {topOfGraph} meters")
        print(f"Highest ever percentage: {highestEverPerc}%")
        print(f"Normal range percentage: {normalRangePerc}%")
        
        # Write the scaled data to a file
        write_downsampled_data(output_file_name, scaled_heights, first_timestamp, last_timestamp)
        
        # Show sample of downsampled data
        print(f"\n=== Sample of downsampled URL data (first 10 points) ===")
        for i, height in enumerate(downsampled_heights[:10]):
            print(f"{i+1}: {height}")
        print("...")
        
        return True
    except Exception as e:
        print(f"Error processing URL data: {e}")
        return False


if __name__ == "__main__":
    # Process local file
    local_file = "Cookham-Lock-height-data.csv"
    process_local_file(local_file)
    
    # Process from URL
    url = "https://check-for-flooding.service.gov.uk/station-csv/7162"
    process_url_data(url)
