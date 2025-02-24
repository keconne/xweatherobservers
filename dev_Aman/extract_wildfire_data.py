#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import pandas as pd

def extract_wildfire_data(json_file, target_event="wildfire"):
    """
    Load the JSON file, filter out only wildfire events, and extract details.

    Returns:
        events_list: A list of dictionaries with summary event details.
        locations_list: A list of dictionaries with each wildfire event's location details.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    events_list = []
    locations_list = []

    # Loop through each record in the JSON file
    for idx, record in enumerate(data):
        source = record.get("_source", {})
        # Filter: only process records where the event type is 'wildfire'
        if source.get("event", "").lower() != target_event.lower():
            continue

        # Assign an event ID (here simply using the loop index + 1)
        event_id = idx + 1

        # Create a dictionary for the event summary
        # We pull out a few key fields (adjust as needed)
        event_detail = {
            "event_id": event_id,
            "event": source.get("event", ""),
            "start_date": source.get("start_date", ""),
            "end_date": source.get("end_date", ""),
            "probability": source.get("probability", ""),
            "severity": source.get("severity", "")
        }

        # Use the first article's details if available
        articles = source.get("articles", [])
        if articles:
            first_article = articles[0]
            event_detail["article_title"] = first_article.get("article_title", "")
            event_detail["article_uri"] = first_article.get("article_uri", "")
            event_detail["summary"] = first_article.get("summary", "")
        else:
            event_detail["article_title"] = ""
            event_detail["article_uri"] = ""
            event_detail["summary"] = ""

        events_list.append(event_detail)

        # Process all locations for this event
        locations = source.get("locations", [])
        for loc in locations:
            location_detail = {
                "event_id": event_id,  # Link the location back to the event
                "location_name": loc.get("name", ""),
                "location_id": loc.get("id", ""),
                "lat": loc.get("location", {}).get("lat", ""),
                "lon": loc.get("location", {}).get("lon", ""),
                "population": loc.get("population", "")
            }
            locations_list.append(location_detail)

    return events_list, locations_list

def write_csvs(events_list, locations_list, event_csv, location_csv):
    """Write the extracted event and location data to CSV files."""
    df_events = pd.DataFrame(events_list)
    df_locations = pd.DataFrame(locations_list)

    df_events.to_csv(event_csv, index=False)
    df_locations.to_csv(location_csv, index=False)
    print(f"Saved wildfire event summary to: {event_csv}")
    print(f"Saved wildfire locations to: {location_csv}")

def main():
    parser = argparse.ArgumentParser(description="Extract wildfire events from JSON and export to CSVs")
    parser.add_argument("--json_file", required=True, help="Path to the JSON file with event data")
    parser.add_argument("--output_event_csv", default="wildfire_events.csv", help="Output CSV for wildfire event summaries")
    parser.add_argument("--output_location_csv", default="wildfire_locations.csv", help="Output CSV for wildfire event locations")
    args = parser.parse_args()

    events_list, locations_list = extract_wildfire_data(args.json_file, target_event="wildfire")
    write_csvs(events_list, locations_list, args.output_event_csv, args.output_location_csv)

if __name__ == "__main__":
    main()
