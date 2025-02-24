#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modular script for converting weather event JSON files to CSV files suitable for gaiaviz

Usage:
    python extract_transform_data.py --json_file path/to/events.json --template_csv path/to/template.csv
       [--node_csv path/to/output_node.csv] [--tag_csv path/to/output_tag.csv]

Flexible: json_config dictionary below defines the keys
and paths in JSON structure. If JSON file’s format changes (e.g. different keys or nested structures),
update the json_config
"""

import argparse
import json
import pandas as pd
import numpy as np
import copy

# Config: Adjust paths/keys if JSON structure changes
json_config = {
    'source_key': '_source',
    'event_key': 'event',
    'articles_key': 'articles',
    'first_article_title_key': 'article_title',
    'locations_key': 'locations',
    'lat_key': ['location', 'lat'],  # list indicating nested keys: e.g., record['location']['lat']
    'lon_key': ['location', 'lon'],
    'population_key': 'population',
    'probability_key': 'probability'
}

# Table ID for events (could also be made an arg)
EVENT_TABLE_ID = 11

# Helper Fxns
def get_nested_value(d, keys, default=None):
    """
    Retrieve a nested value from dictionary d using a list of keys.
    """
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default
    return d

def load_json(json_file):
    """Load and return the JSON data from a file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def process_events(data, template_df, config):
    """
    Process JSON event records and generate node and tag records

    Parameters:
        data (list): List of event records from the JSON
        template_df (DataFrame): The template CSV loaded as a DataFrame
        config (dict): Configuration mapping for JSON keys

    Returns:
        node_list (list): List of node dictionaries
        tag_list (list): List of tag dictionaries
    """
    # Convert entire template to list of dictionaries (for node copying)
    node_template_list = template_df.to_dict('records')
    
    # Set number of base nodes (assumed to be first N rows)
    rootTree = 6
    baseNodes = template_df.head(rootTree).to_dict('records')
    
    # Start with base nodes for node list
    node_list = copy.deepcopy(baseNodes)
    
    # Create sorted list of unique event types based on config
    events = list({ rec[config['source_key']][config['event_key']] for rec in data })
    events.sort()
    
    tag_list = []
    
    # Initialize nodeID from last base node (assuming 'np_node_id' exists)
    nodeID = node_list[-1]['np_node_id'] if 'np_node_id' in node_list[-1] else len(node_list)
    
    # Process each event record inJSON
    for i, record in enumerate(data):
        source = record.get(config['source_key'], {})
        event_type = source.get(config['event_key'], 'unknown')
        event_cat = events.index(event_type)
        
        # Create tag record using first article title
        articles = source.get(config['articles_key'], [])
        first_article_title = articles[0].get(config['first_article_title_key'], '') if articles else ''
        tag_list.append({
            'record_id': i + 1,
            'table_id': EVENT_TABLE_ID,
            'title': event_type,
            'description': first_article_title
        })
        

        # Create the main event node
        # Copy a template node to serve as event node (using a base node copy)
        event_node = copy.deepcopy(node_template_list[rootTree])
        nodeID += 1
        event_node['np_node_id'] = nodeID
        event_node['parent_id'] = 0
        event_node['np_table_id'] = EVENT_TABLE_ID
        event_node['record_id'] = i + 1
        
        # Use first location’s lat/lon (if available)
        locations = source.get(config['locations_key'], [])
        if locations:
            first_loc = locations[0]
            lat = get_nested_value(first_loc, config['lat_key'], 0.0)
            lon = get_nested_value(first_loc, config['lon_key'], 0.0)
            if lat != 0.0 or lon != 0.0:
                event_node['translate_x'] = lon
                event_node['translate_y'] = lat
            else:
                # Auto-distribute if coordinates invalid
                event_node['translate_x'] = event_node.get('translate_x', 0) + i * 2.0
                event_node['translate_y'] = event_node.get('translate_y', 0) + i * 100.0
        else:
            # Fallback: use default or auto-distribute if no location provided
            event_node['translate_x'] = event_node.get('translate_x', 0) + i * 2.0
            event_node['translate_y'] = event_node.get('translate_y', 0) + i * 100.0
        
        event_node['translate_z'] = -10.0
        
        # Set transparency based on probability (scaled from 0.0-1.0 to 0-255)
        probability = source.get(config['probability_key'], 0.0)
        probA = int(probability * 255)
        event_node['color_a'] = min(probA, 255)
        
        # Set texture id based on event category (arbitrary offset of 1)
        event_node['np_texture_id'] = event_cat + 1
        
        # Reserve the position in the node_list for later centroid adjustment
        event_node_index = len(node_list)
        node_list.append(event_node)
        
        # For calculating centroid
        lat_sum = 0.0
        lon_sum = 0.0
        num_locs = len(locations) if locations else 0
        
        # Process each location within event
        for j, loc in enumerate(locations):
            location_node = copy.deepcopy(node_template_list[rootTree])
            nodeID += 1
            location_node['np_node_id'] = nodeID
            location_node['parent_id'] = 0  # Or set differently if hierarchy desired
            location_node['np_table_id'] = EVENT_TABLE_ID
            location_node['record_id'] = i + 1
            
            # Extract lat/lon from the location record (using nested keys)
            lat = get_nested_value(loc, config['lat_key'], 0.0)
            lon = get_nested_value(loc, config['lon_key'], 0.0)
            lat_sum += lat
            lon_sum += lon
            
            if lat != 0.0 or lon != 0.0:
                location_node['translate_x'] = lon
                location_node['translate_y'] = lat
            else:
                # Adjust if the coordinates invalid
                location_node['translate_x'] = location_node.get('translate_x', 0) + i * 5.0
                
            # Set a color attribute based on event category
            location_node['np_color_id'] = event_cat
            probB = int(probability * 255)
            location_node['color_a'] = min(probB, 255)
            
            # Scale based on population (using a configurable factor)
            pop = loc.get(config['population_key'], 0)
            scale_factor = np.sqrt(pop * 0.00002)
            location_node['scale_x'] = 0.2
            location_node['scale_y'] = 0.2
            location_node['scale_z'] = scale_factor
            
            node_list.append(location_node)
            
            # Create link node connecting event and location
            link_node = copy.deepcopy(node_template_list[rootTree])
            nodeID += 1
            link_node['np_node_id'] = nodeID
            link_node['parent_id'] = event_node['np_node_id']  # Link to main event node
            link_node['type'] = 7  # Assuming type 7 indicates a link node
            # The child_id set to previous node (the location node just created)
            link_node['child_id'] = nodeID - 1
            link_node['np_geometry_id'] = 3
            link_node['np_color_id'] = event_cat
            link_node['np_table_id'] = EVENT_TABLE_ID
            link_node['record_id'] = i + 1
            
            node_list.append(link_node)
        
        # Adjust event node's position to be centroid of all its locations.
        if num_locs > 0:
            event_node['translate_x'] = lon_sum / num_locs
            event_node['translate_y'] = lat_sum / num_locs
            # Update the node in list
            node_list[event_node_index] = event_node
    
    return node_list, tag_list

def write_csv_files(node_list, tag_list, node_csv, tag_csv):
    """Write the node and tag records to CSV files."""
    nodes_df = pd.DataFrame.from_records(node_list)
    tags_df = pd.DataFrame.from_records(tag_list)
    
    nodes_df.to_csv(node_csv, index=False)
    tags_df.to_csv(tag_csv, index=False)
    print(f"Saved nodes to: {node_csv}")
    print(f"Saved tags to: {tag_csv}")

# Main Function
def main(args):
    # Load node template CSV
    template_df = pd.read_csv(args.template_csv)
    
    # Load JSON data
    data = load_json(args.json_file)
    
    # Process events to generate nodes and tags
    node_list, tag_list = process_events(data, template_df, json_config)
    
    # Write output CSV files
    write_csv_files(node_list, tag_list, args.node_csv, args.tag_csv)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert weather event JSON to CSV for 3D visualization.")
    parser.add_argument("--json_file", required=True, help="Path to the input JSON file containing event data.")
    parser.add_argument("--template_csv", required=True, help="Path to the node template CSV file.")
    parser.add_argument("--node_csv", default="output_node.csv", help="Path for the output node CSV file.")
    parser.add_argument("--tag_csv", default="output_tag.csv", help="Path for the output tag CSV file.")
    
    args = parser.parse_args()
    main(args)
