import json
from datetime import datetime
import pandas as pd
from collections import Counter

# Sample JSON data (usually you would load this from a file)
with open('xWeather_Erasmus_US_250.json', 'r') as file:
    data = json.load(file)

# Loop through each entry in the list to extract start_date and end_date
for entry in data:
    event = entry['_source']
    
    # Extracting start_date and end_date
    start_date = event['start_date']
    end_date = event['end_date']
    
    # Convert the string dates to datetime objects if needed
    start_date_obj = datetime.fromisoformat(start_date)
    end_date_obj = datetime.fromisoformat(end_date)
    
    # Print the extracted dates
    #print(f"Start Date: {start_date_obj}")
    #print(f"End Date: {end_date_obj}")

# Initialize variables for tracking the oldest start date and newest end date
oldest_start_date = None
newest_end_date = None

# Loop through each entry in the list to extract start_date and end_date
for entry in data:
    event = entry['_source']
    
    # Extracting start_date and end_date
    start_date = event['start_date']
    end_date = event['end_date']
    
    # Convert the string dates to datetime objects
    start_date_obj = datetime.fromisoformat(start_date)
    end_date_obj = datetime.fromisoformat(end_date)
    
    # Update the oldest start date
    if oldest_start_date is None or start_date_obj < oldest_start_date:
        oldest_start_date = start_date_obj
    
    # Update the newest end date
    if newest_end_date is None or end_date_obj > newest_end_date:
        newest_end_date = end_date_obj

# Print the results
print(f"Oldest Start Date: {oldest_start_date}")
print(f"Newest End Date: {newest_end_date}")

#####################################################################################################
#DATA QUALITY
# Function to evaluate data quality
def evaluate_data_quality(data):
    errors = []

    for event in data:
        source = event.get("_source", {})
        
        # 1. Check if all required keys are present
        if not source.get("event") or not source.get("start_date") or not source.get("end_date"):
            errors.append("Missing essential fields (event, start_date, end_date).")
        
        # 2. Check if event_date is valid
        try:
            event_date = source.get("articles", [])[0].get("event_date", None)
            if event_date:
                datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            errors.append(f"Invalid event_date format for event {source.get('event')}.")
        
        # 3. Check if severity and probability are valid
        if not (0 <= source.get("probability", 0) <= 1):
            errors.append(f"Invalid probability value for event {source.get('event')}.")
        if not (0 <= source.get("severity", 0) <= 5):  # assuming severity is between 0 and 5
            errors.append(f"Invalid severity value for event {source.get('event')}.")
        
        # 4. Check if location coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)
        location = source.get("locations", [])[0].get("location", {})
        lat = location.get("lat", None)
        lon = location.get("lon", None)
        if lat is not None and (lat < -90 or lat > 90):
            errors.append(f"Invalid latitude for location {source.get('country')}.")
        if lon is not None and (lon < -180 or lon > 180):
            errors.append(f"Invalid longitude for location {source.get('country')}.")

        # 5. Check if article URLs are well-formed
        article_uri = source.get("articles", [])[0].get("article_uri", "")
        if article_uri and not article_uri.startswith("http"):
            errors.append(f"Invalid article URI for event {source.get('event')}.")

    return errors

# Evaluate data quality
errors = evaluate_data_quality(data)

# Print results
if errors:
    for error in errors:
        print(f"Error: {error}")
else:
    print("The data is of good quality!")

######################################################################################
#COMPLETENESS
# Function to check for nulls in the data
def check_for_nulls(data):
    nulls = []

    def find_nulls(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                find_nulls(value, f"{path}/{key}")
        elif isinstance(obj, list):
            for idx, value in enumerate(obj):
                find_nulls(value, f"{path}/{idx}")
        elif obj is None:
            nulls.append(path)
    
    # Start checking from the root of the data
    for event in data:
        find_nulls(event)
    
    return nulls

# Check for nulls
nulls_found = check_for_nulls(data)

# Print results
if nulls_found:
    print("Null values found at the following paths:")
    for path in nulls_found:
        print(path)
else:
    print("No null values found.")

###########################################################################################
#UNIQUENESS
# Extract _id values
ids = [event["_id"] for event in data]

# Use Counter to count occurrences of each _id
id_counts = Counter(ids)

# Check for duplicates (any _id with count > 1)
duplicates = {id: count for id, count in id_counts.items() if count > 1}

if duplicates:
    print("There are duplicate _id values:", duplicates)
else:
    print("All _id values are unique.")

###########################################################################################
#DATA TYPE CONSISTENCY
# Check if 'event_date' is in the correct datetime format and 'probability' is a float between 0 and 1
# for event in data:
#     event_date = event["_source"]["articles"][0]["event_date"]
#     probability = event["_source"]["articles"][0]["probability"]
    
#     # Check if event_date is a valid date
#     try:
#         datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S.%f")
#         print(f"Valid event_date: {event_date}")
#     except ValueError:
#         print(f"Invalid event_date: {event_date}")
    
#     # Check if probability is a float between 0 and 1
#     if isinstance(probability, float) and 0 <= probability <= 1:
#         print(f"Valid probability: {probability}")
#     else:
#         print(f"Invalid probability: {probability}")



# Check if lat and lon are within valid ranges
# for event in data:
#     lat = event["_source"]["locations"][0]["location"]["lat"]
#     lon = event["_source"]["locations"][0]["location"]["lon"]
    
#     # Check latitude
#     if -90 <= lat <= 90:
#         print(f"Valid latitude: {lat}")
#     else:
#         print(f"Invalid latitude: {lat}")

#         # Check longitude
#     if -180 <= lon <= 180:
#         print(f"Valid longitude: {lon}")
#     else:
#         print(f"Invalid longitude: {lon}")

# Check logical consistency for start_date and end_date
for event in data:
    start_date = event["_source"].get("start_date")
    end_date = event["_source"].get("end_date")
    
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f")
        
        if start_datetime > end_datetime:
            print(f"Invalid date range: start_date ({start_date}) is after end_date ({end_date})")