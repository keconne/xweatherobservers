import pandas as pd
import json

# read json file
with open("xWeather_Erasmus_US_250.json", "r") as file:
    data = json.load(file)

# initialize lists
names = []
ids = []
lats = []
lons = []
populations = []
numbers = []
scores = []
parent_countries = []
parents = []
successes = []
is_alternames = []
records = []
# parse all locations
for i in range(0,len(data)):
    records.append(i)
    nest1 = data[i].get('_source', {})
    nested_locations = nest1.get('locations', [])
    for location in nested_locations:
        names.append(location.get('name'))
        ids.append(location.get('id'))
        coords = location.get('location', {})
        lats.append(coords.get('lat'))
        lons.append(coords.get('lon'))
        populations.append(location.get('population'))
        numbers.append(location.get('number'))
        scores.append(location.get('score'))
        parent_countries.append(location.get('parent_country'))
        parents.append(location.get('parent'))
        successes.append(location.get('success'))
        is_alternames.append(location.get('is_altername'))

locations = pd.DataFrame({
    'name':names,
    'id':ids,
    'lat':lats,
    'lon':lons,
    'population':populations,
    'number':numbers,
    'score':scores,
    'parent_country':parent_countries,
    'success':successes,
    'is_altername':is_alternames
})

# unique-ness of locations
locations.name.drop_duplicates()
locations.id.drop_duplicates()
locations.drop_duplicates()

locations[['lat', 'lon']].value_counts()
locations[['name', 'lat', 'lon', 'population', 'parent_country', 'id']].drop_duplicates()

# at least in our sample, these fields are consistent for locations across records
locations[['id', 'name', 'lat', 'lon', 'population', 'parent_country', 'success']].value_counts()


