import pandas as pd
import json

with open("xWeather_Erasmus_US_250.json", "r") as file:
    data = json.load(file)

def extract_field(
        data, 
        field_name,
        in_source = True, 
        in_articles = False,
        in_locations = False,
        return_index = False):
    values = []
    records = []
    for i in range(0,len(data)):
        records.append(i)
        if in_source:
            nest1 = data[i].get('_source', {})
            if in_articles:
                nested_articles = nest1.get('articles', [])
                for article in nested_articles:
                    values.append(article.get(field_name))
            elif in_locations:
                nested_locations = nest1.get('locations', [])
                for location in nested_locations:
                    values.append(location.get(field_name))
            else:
                values.append(nest1.get(field_name))
        else:
            values.append(data[i].get(field_name))
    if return_index:
        return records, values
    else:
        return values


# 1) is _index == 'event_database' for all records?
all__index_values = extract_field(data, '_index', False)
set(all__index_values)


# 2) is how is _score derived? 
all__scores = extract_field(data, '_score', False)
set(all__scores)

# 3) are there instances of _source being a list of dictionaries or is it always 1-1? 


# 4) is article_index the same for all records?


# 5) how is the proability field in the articles dict derived?


# 6) confirm definition for the severity field in the articles dict?


# 7) how/is the _source-level probability field tied to the articles probability?
# exact match of the _source-level probability field. And only one article. _source-level may be an aggregate of article probabilities



# 8) how/is the _source-level score field tied to the articles score?


# 9) how/is the _source-level severity field tied to the articles severity?


# 10) is the _source-level country field ever a list?


# 11) explore runner-up data to guess definition


# 12) explore success data to guess definition

