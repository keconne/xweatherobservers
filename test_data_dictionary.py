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
        if in_source:
            nest1 = data[i].get('_source', {})
            if in_articles:
                nested_articles = nest1.get('articles', [])
                for article in nested_articles:
                    vals = article.get(field_name)
                    recs = [i]*len(vals) if type(vals) == list else i
                    values.append(vals)
                    records.append(recs)
            elif in_locations:
                nested_locations = nest1.get('locations', [])
                for location in nested_locations:
                    vals = location.get(field_name)
                    recs = [i]*len(vals) if type(vals) == list else i
                    values.append(vals)
                    records.append(recs)
            else:
                vals = nest1.get(field_name)
                recs = [i]*len(vals) if type(vals) == list else i
                values.append(vals)
                records.append(recs)
        else:
            vals = data[i].get(field_name)
            recs = [i]*len(vals) if type(vals) == list else i
            values.append(vals)
            records.append(recs)
            
    if return_index:
        return pd.DataFrame({'record_id':records, field_name:values})
    else:
        return values


# 1) is _index == 'event_database' for all records?
all__index_values = extract_field(data, '_index', False)
set(all__index_values)


# 2) is how is _score derived? 
all__scores = extract_field(data, '_score', False)
set(all__scores)

# 3) are there instances of _source being a list of dictionaries or is it always 1-1? 
all__source = extract_field(data, '_source', False)
n_fields_in_source = [len(all__source[index]) for index, value in enumerate(all__source)]
set(n_fields_in_source)

# 4) is article_index the same for all records?
all_article_index = extract_field(data, 'article_index', True, True)
set(all_article_index)

#------------------------------------------------------------------------------------------
# 5) how is the proability field in the articles dict derived?
df5 = extract_field(data, 'probability', True, True, return_index = True)
df5.probability.quantile([0, .25, .5, .75, 1])
df5.probability.drop_duplicates()

# low scores
df5[df5.probability < .1]
data[86] # long academic analysis of a biblical civilization's response to a 3-year drought.
# locations are all tied to the university different participating researchers are affiliated with
data[89] # 2/4 articles have low probability
# one is long-winded and the summary is erratic, but doesn't seem too different from the others in this record by content
# The other is unique in that it recaps a testimony to congress, but it's directly relevant to the flood
data[103] # starting to think it may be focused more on time and place than content
# the low probability article here (1/4) is in a different location a month later than the other articles
data[108] # 1 article only. Trivia post with minimal mention the weather event.


#------------------------------------------------------------------------------------------
# 6) confirm definition for the severity field in the articles dict?
df6 = extract_field(data, 'severity', True, True, return_index = True)
non_zero_severity = df6[df6.severity > 0].record_id.drop_duplicates()
all_events = extract_field(data, 'event', True, return_index = True)

# can all weather events have severity score?
set(all_events[all_events.record_id.isin(non_zero_severity)].event).difference(set(all_events.event))
set(all_events.event).difference(set(all_events[all_events.record_id.isin(non_zero_severity)].event))

# distribution
df6.severity.quantile([0, .25, .5, .75, 1])

# top scores
df6[df6.severity > .3]
data[88] # 2/2 articles were high severity. 
# Both mention '36-year drought' referring to a sports team making postseason
data[186] # 1/1 article was high severity.
# Mentions 34 counties warned of wildfire risk
df6[df6.severity > .25]
data[172] # 2/125 articles were high severity 
# 1 uses strong descriptors including 'devastating', 'severe (2x)', and 'bomb cyclone'
# 1 article is very long with redundant descriptions of widespread drought for prolonged periods

# low scores
df6[df6.severity == 0]
data[0] # 1 article
# mentions 'wildfire spread across at least 10 counties'
# population numbers in the millions for some locations
# unclear why severity is so low compared to high severity articles
data[1]
# article uses strong descriptors such as 'life-threatening', 'flood emergency', etc.
# talks about widespread damage across a large region. Includes 9 locations, high populations
# arguably more severe than the articles in record 172 based on text and extracted metadata

# low but not 0
df6[(df6.severity > 0) & (df6.severity < .01)]
data[62] # 1/1 article was low severity (but not 0)
# fitting descriptors for low severity such as 'good news', 'looks a lot better', etc.
data[117] # 1/8 articles with extremely low severity (not 0)
# less obvious case than in record 62, but uses very uncertain language;
# 'some of the rain could...', 'the biggest issue may be', 'minor coastal flooding is likely'
# certain language used is not severe;
# 'warm air will be flooding in', 'north beaches will not be subjected to any flooding'
data[196] # 1/n articles with extremely low severity (not 0)
# uncertain language is the only potential indicator
# 'storm could hit', 'details still not totally clear'
data[201] # mentions some real impacts of extreme weather, but article focuses
# on the benefits of a resulting federal program 'reducing inflation and increasing jobs
data[217] # short article, improved plowing 'sharply reduced cancellations and delays'

#------------------------------------------------------------------------------------------
# 7) confirm definition for the score field in the locations dict
df7 = extract_field(data, 'score', True, False, True, return_index = True)
df7.score.quantile([0, .25, .5, .75, 1])
df7[df7.score < .075]
data[2] # Madison and Jackson have low scores. Since they are also people names?
# Transylvania County has a 1.0 score from the same record. Clearly a place
# 0000197326
data[33] # Jackson again. Has the same exact score as in 2nd record
# 0000197326
data[48] # Ashland

# distribution of place names
locations = pd.read_csv("locations.csv")
locations[['id', 'name', 'score']].sort_values('score').drop_duplicates()
locations[['id', 'name', 'score', 'number']].sort_values('score').drop_duplicates()
locations[['id', 'name', 'score']].value_counts()


#------------------------------------------------------------------------------------------
# 8) confirm definition for the number field in the locations dict
# is it number of times appeared total?
locations[locations.name=='Tennessee'] # no

# is it number of records appeared total (multiple appearances in one record counts as 1)?
df8 = extract_field(data, 'number', True, False, True, True)
location_ids = extract_field(data, 'id', True, False, True, True)
df8 = df8.merge(location_ids, how = 'left', on = 'record_id')
records_appeared_totals = df8[['record_id', 'id']].drop_duplicates().id.value_counts().to_frame().reset_index()
records_appeared_totals.merge(df8[['id', 'number']].drop_duplicates(), how = 'left')

# number can vary at the record-level
locations['id'].drop_duplicates()
locations[['id', 'number']].drop_duplicates()

# is it number of times appeared in article?
data[0] # North appears 15 times, but includes title, video title, and footer, so maybe 12 is accurate
# South Carolina appears once, correct
# Tennessee appears once, number claims twice, incorrect
# Kentucky appears once, number claims three time, incorrect
# Washington appears twice, number claims eight times, incorrect
data[100] 
# San Benito County appears 10 times, number is missing from data
data[200]
# more inconsistencies.
# definitely pulls from article because many locations never appear in summary
# number doesn't seem to reflect the number of times the location is referenced


#------------------------------------------------------------------------------------------
# 9) confirm definition for the success field in the locations dict
df9 = extract_field(data, 'success', True, False, True, True)
df9.drop_duplicates()
df9.success.drop_duplicates()

#------------------------------------------------------------------------------------------
# 10) how/is the _source-level probability field tied to the articles probability?
# exact match of the _source-level probability field. And only one article. _source-level may be an aggregate of article probabilities
df10 = extract_field(data, 'probability', True, return_index = True)
df10['articles_mean'] = df5.groupby('id').mean()
df10['articles_median'] = df5.groupby('id').median()
df10['articles_sum'] = df5.groupby('id').sum()
df10.sort_values(by = 'probability')
df10.sort_values(by = 'articles_sum')
# at a glance, articles are ranked equally whether by probability or sum


#------------------------------------------------------------------------------------------
# 11) how/is the _source-level score field tied to the locations score?
df11 = extract_field(data, 'score', True, return_index = True)
df11.score.quantile([0, .25, .5, .75, 1])
df11 = df11[~df11.score.isnull()]
df7_notnull = df7[~df7.score.isnull()]
df11['location_mean'] = df7_notnull.groupby('id').mean()
df11['location_median'] = df7_notnull.groupby('id').median()
df11['location_sum'] = df7_notnull.groupby('id').sum()
df11.sort_values(by = 'score')
df11.sort_values(by = 'location_sum')


#------------------------------------------------------------------------------------------
# 12) how/is the _source-level severity field tied to the articles severity?
df12 = extract_field(data, 'severity', True, return_index = True)
df12['articles_mean'] = df6.groupby('id').mean()
df12['articles_median'] = df6.groupby('id').median()
df12['articles_sum'] = df6.groupby('id').sum()
df12.sort_values(by = 'severity')
df12.sort_values(by = 'articles_sum')
# at a glance, articles are ranked equally whether by severity or sum


#------------------------------------------------------------------------------------------
# 13) is the _source-level country field ever a list?
countries_per_record = extract_field(data, 'country', True, return_index = True).id.value_counts()
len(countries_per_record[countries_per_record > 1]) # not in sample


#-----------------------------------------------------------------------------------------
# 14) explore runner-up data to guess definition
df14 =  extract_field(data, 'runner_up', True, False, False, return_index = True)
df14.merge(df12).merge(df11).merge(df10)

#-----------------------------------------------------------------------------------------
# 15) explore is_altername definition
df15 = extract_field(data, 'is_altername', True, False, True, return_index = True)
df15[df15.is_altername]
data[13] # Louisiana, 0000203829
data[27] # District of Columbia. 0000199788

data[113] # North Carolina, 0000209473
# NC in link to related article
data[200] # Louisiana, 0000203829
# only mention of Louisiana is 'Lafayette, LA' associated with the author

locations[locations.name == 'Louisiana']
locations[locations.name == 'District of Columbia']
locations[locations.name == 'North Carolina']