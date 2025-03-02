# -*- coding: utf-8 -*-

___copyright___ = "Copyright 2025 Shane Saxon"
___license___ = "Apache-2.0"

import pandas as pd
import numpy as np
import json

# Template node table (inherent params and easy way to format CSV fields)
nodeTemplate = pd.read_csv("./xWeather-Gz/py+data/xWeather_template/csv/xWeather_template_np_node.csv")    # glyph default tree

#Load in Color key
colorKey = pd.read_csv("./EventToColor.csv")

# Copy template base node (null node, 4 cams & root grid)
rootTree = 6
baseNodes = nodeTemplate.head(rootTree)
nodeList = baseNodes.to_dict('records')  # this process creates correct CSV field types

nodeTree = nodeTemplate.to_dict('records')

# Load the JSON data
with open('./xWeather-Gz/py+data/xWeather_Erasmus_US_250.json', "r") as file:
    data = json.load(file)

# === Modification 1: Filter to only include wildfire events ===
#or record['_source']['event'].lower() == "flood"
data = [record for record in data if record['_source']['event'].lower() == "wildfire"]

events = []
for i in range(len(data)):
    events.append(data[i]['_source']['event'])
# Remove redundancies (now should only be "wildfire")
events = list(set(events))
events = sorted(events)
#print(events)

tags = []
eventTblID = 7  # assign a unique (arbitrary) table_id

nodeID = nodeList[-1]['np_node_id']  # starting id from last base node
parentID = 0  # link A-end
childID = 0   # link B-end

# Loop through all events to create the node and tag tables
for i in range(len(data)):
    # get eventCat number (in this case there will be only one, "wildfire")
    eventCat = events.index(data[i]['_source']['event'])
    colorEvents = colorKey['Weather Event'].tolist()
    colorIndex = colorEvents.index(data[i]['_source']['event'])
    
    tags.append({
        'np_tag_id': i+1,
        'record_id': i+1,
        'table_id': eventTblID,
        'title': data[i]['_source']['event'],
        'description': data[i]['_source']['articles'][0]['article_title']
    })
    
    # event node (links to event location node layer)
    nodeList.append(nodeTree[rootTree].copy())
    
    # increment id's
    nodeID += 1  
    parentID = 0        # root node's have parent_id = 0
    eventID = nodeID
    eventIndex = len(nodeList)
    
    # apply id's to the event node
    nodeList[-1]['np_node_id'] = nodeID
    nodeList[-1]['parent_id'] = parentID
    nodeList[-1]['np_table_id'] = eventTblID
    nodeList[-1]['record_id'] = i+1  # or use nodeID
    
    # lat/long, unless 0,0 in which case auto-distribute
    lat = data[i]['_source']['locations'][0]['location']['lat']
    lon = data[i]['_source']['locations'][0]['location']['lon']
    
    if lat != 0.0 or lon != 0.0:
        nodeList[-1]['translate_x'] = lon
        nodeList[-1]['translate_y'] = lat
    else:
        nodeList[-1]['translate_x'] += i * 2.0
        nodeList[-1]['translate_y'] += i * 100.0
        
    nodeList[-1]['translate_z'] = -10.0
    
    probA = int(data[i]['_source']['probability'] * 255)
    if probA > 255:
        probA = 255
    nodeList[-1]['color_a'] = probA  # transparency
    nodeList[-1]['np_texture_id'] = eventCat + 1
    
    # event centroid calculation
    locNum = len(data[i]['_source']['locations'])
    latAvg = 0.0
    lonAvg = 0.0 
      
    for j in range(locNum):
        # create event location node
        # can choose different rows from temp for set values for nodes/glyphs
        nodeList.append(nodeTree[rootTree].copy())
       
        nodeID += 1  
        parentID = 0        # root
        L1 = nodeID
        
        # set the id's for the location node
        nodeList[-1]['np_node_id'] = nodeID
        nodeList[-1]['parent_id'] = parentID
        nodeList[-1]['np_table_id'] = eventTblID
        nodeList[-1]['record_id'] = i+1

        lat = data[i]['_source']['locations'][j]['location']['lat']
        latAvg += lat
        lon = data[i]['_source']['locations'][j]['location']['lon']
        lonAvg += lon
        
        if lat != 0.0 or lon != 0.0:
            nodeList[-1]['translate_x'] = lon
            nodeList[-1]['translate_y'] = lat
        else:
            nodeList[-1]['translate_x'] += i * 5.0
        
        # manually modify nodes in app, then identify what attributes modified and change here
        #np_topo_id for changing node type
        #modify xWeather_template file to affect whole doc
        # modify color for diff weather types for easy dinstinction
        # event specific node attributes
        nodeList[-1]['np_color_id'] = eventCat
        probB = int(data[i]['_source']['probability'] * 255)
        if probB > 255:
            probB = 255
        nodeList[-1]['color_a'] = probB
        nodeList[-1]['color_r'] = colorKey.iloc[colorIndex]['R']
        nodeList[-1]['color_g'] = colorKey.iloc[colorIndex]['G']
        nodeList[-1]['color_b'] = colorKey.iloc[colorIndex]['B']
        
        popu = data[i]['_source']['locations'][j]['population'] * 0.00002
        popu = np.sqrt(popu)
        nodeList[-1]['scale_x'] = 0.2
        nodeList[-1]['scale_y'] = 0.2
        nodeList[-1]['scale_z'] = popu
        
        # create a link node
        nodeList.append(nodeTree[rootTree].copy())
       
        nodeID += 1  
        parentID = eventID
        
        nodeList[-1]['np_node_id'] = nodeID
        nodeList[-1]['parent_id'] = parentID
        
        nodeList[-1]['type'] = 7
        nodeList[-1]['child_id'] = nodeID - 1
        
        nodeList[-1]['np_geometry_id'] = 3     
        nodeList[-1]['np_color_id'] = eventCat
        nodeList[-1]['np_table_id'] = eventTblID
        nodeList[-1]['record_id'] = i   # nodeID

    nodeList[eventIndex - 1]['translate_x'] = lonAvg / locNum
    nodeList[eventIndex - 1]['translate_y'] = latAvg / locNum

# === Modification 2: Change output paths to save to dev_Aman folder with new filenames ===

nodeFilePath = "./WildfireTesting/csv/wildfire_np_node.csv"
print("Save: " + nodeFilePath)
nodes = pd.DataFrame.from_records(nodeList)
nodes.to_csv(nodeFilePath, index=False)

tagFilePath = "./WildfireTesting/csv/wildfire_np_tag.csv"
print("Save: " + tagFilePath)
tagsDF = pd.DataFrame.from_records(tags)
tagsDF.to_csv(tagFilePath, index=False)
