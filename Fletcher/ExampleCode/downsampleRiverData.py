#!/usr/bin/env python3
# downsampleRiverData.py - Downsample river level data using LTTB algorithm

from datetime import datetime
import csv
import math
from LTTBalgrithm import largest_triangle_three_buckets

def downsample_river_data(data_tuples, first_timestamp, last_timestamp, threshold=200):
    """
    Downsample river level data using the Largest Triangle Three Buckets algorithm.
    
    Args:
        data_tuples: List of tuples (row_number, height)
        first_timestamp: Datetime object representing the first timestamp
        last_timestamp: Datetime object representing the last timestamp
        threshold: Number of data points in the downsampled result (default 200)
        
    Returns:
        List of downsampled height values
    """
    # The LTTB algorithm expects data in format [(x,y), (x,y), ...] where x is row number and y is height
    downsampled_tuples = largest_triangle_three_buckets(data_tuples, threshold)
    
    # Extract just the height values (second element of each tuple)
    downsampled_heights = [t[1] for t in downsampled_tuples]
    
    return downsampled_heights

def write_downsampled_data(output_file, heights, first_timestamp, last_timestamp, topOfGraph, highestEverPerc, normalRangePerc):
    """
    Write the downsampled data to a file.
    First line: first timestamp
    Second line: last timestamp
    Remaining lines: height values (one per line)
    
    Args:
        output_file: Path to output file
        heights: List of downsampled height values
        first_timestamp: Datetime object representing the first timestamp
        last_timestamp: Datetime object representing the last timestamp
    """
    with open(output_file, 'w', newline='') as f:
        # Write timestamps in human-readable format (hh:mm ddd mm)
        f.write(f"{first_timestamp.strftime('%H:%M %a %d')}\n")
        f.write(f"{last_timestamp.strftime('%H:%M %a %d')}\n")
        f.write(f"{topOfGraph}\n")
        f.write(f"{highestEverPerc}\n")
        f.write(f"{normalRangePerc}\n")
        
        # Write each height value on a separate line
        for height in heights:
            f.write(f"{height}\n")
            
    print(f"Downsampled data written to {output_file}")
    print(f"First timestamp: {first_timestamp.strftime('%H:%M %a %d')}")
    print(f"Last timestamp: {last_timestamp.strftime('%H:%M %a %d')}")
    print(f"Number of data points: {len(heights)}")
    print(f"Time range: {last_timestamp - first_timestamp}")

def scaleValues(highestEverHeight, topOfNormalRange, heights):
    """
    Scale river height values to percentage values for graph rendering.
    
    Args:
        highestEverHeight: Highest ever recorded height in meters (float)
        topOfNormalRange: Top of normal range height in meters (float)
        heights: List of river heights in meters (list of floats)
    
    Returns:
        tuple: (
            topOfGraph: Height value for top of graph in meters (float),
            highestEverPercentage: Percentage for highest ever height (int),
            normalRangePercentage: Percentage for top of normal range (int),
            heightPercentages: List of percentage values for input heights (list of ints)
        )
    """
    # Calculate the top of graph value (round to nearest 0.5m and ensure it's higher than highestEverHeight)
    
    # Round to nearest 0.5
    topOfGraph = math.ceil(highestEverHeight * 2) / 2
    
    # Calculate percentages (as proportion of topOfGraph)
    highestEverPercentage = round((highestEverHeight / topOfGraph) * 100)
    normalRangePercentage = round((topOfNormalRange / topOfGraph) * 100)
    
    # Calculate percentages for all heights
    heightPercentages = [round((height / topOfGraph) * 100) for height in heights]
    
    return (topOfGraph, highestEverPercentage, normalRangePercentage, heightPercentages)

# Main guard method removed - now used as a module
