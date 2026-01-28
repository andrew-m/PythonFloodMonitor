#!/usr/bin/env python3
# fetchRiverData.py - Fetch and parse river level data from CSV files and URLs

import csv
import io
from datetime import datetime

# Check if requests module is available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def fetch_river_data_from_file(file_path):
    """
    Open a local CSV file and return a file stream.
    
    Args:
        file_path (str): Path to the local CSV file
        
    Returns:
        file: A file-like object containing CSV data
    """
    return open(file_path, 'r')


def fetch_river_data_from_url(url):
    """
    Fetch CSV data from a URL and return a file-like stream.
    
    Args:
        url (str): URL of the CSV file to fetch
        
    Returns:
        file-like: A file-like object containing CSV data
        
    Raises:
        RuntimeError: If requests module is not available
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError("The 'requests' module is not installed. Install it with 'pip install requests' to use URL functionality.")
        
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return io.StringIO(response.text)


def fetch_river_data(csv_stream):
    """
    Process river level data from a CSV stream.
    Extract tuples of (row_number, height) from CSV data.
    Standard format is 2-column (timestamp, height).
    Row numbers are generated sequentially.
    
    Args:
        csv_stream: A file-like object containing CSV data
        
    Returns:
        tuple: (data_tuples, first_timestamp, last_timestamp)
    """
    data_tuples = []
    first_timestamp = None
    last_timestamp = None
    
    # Skip header row
    next(csv_stream)
    
    # Process data rows
    row_counter = 1  # Generate sequential row numbers
    csv_reader = csv.reader(csv_stream)
    for row in csv_reader:
        if not row or len(row) < 2:  # Skip empty or invalid rows
            continue
            
        # Extract timestamp and height from the CSV
        timestamp_str = row[0]
        height = float(row[1])
        
        # Use sequential row numbering
        row_number = row_counter
        row_counter += 1
        
        # Store first and last timestamps
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        if first_timestamp is None:
            first_timestamp = timestamp
        last_timestamp = timestamp
        
        # Create tuple (row_number, height) and add to our list
        data_tuples.append((row_number, height))
    
    print(f"First timestamp: {first_timestamp}")
    print(f"Last timestamp: {last_timestamp}")
    print(f"Total data points: {len(data_tuples)}")
    print("Array of tuples (first 10 shown):")
    for i, tup in enumerate(data_tuples[:10]):
        print(tup)
    print("...")
    
    return data_tuples, first_timestamp, last_timestamp

# Main guard method removed - now used as a module
