# -*- coding: utf-8 -*-

___copyright___ = "Copyright 2025 Shane Saxon"
___license___ = "Apache-2.0"

#from datetime import datetime as dt
#startTime = dt.now()                # Handy for optimizing execution time

import pandas as pd
import numpy as np
import json


# Template node table (inherent params and easy way to format CSV fields)
nodeTemplate = pd.read_csv("xWeather_template/csv/xWeather_template_np_node.csv")    # glyph default tree

# Copy template base node (null node, 4 cams & root grid)
rootTree = 6
baseNodes = nodeTemplate.head(rootTree)
nodeList = baseNodes.to_dict('records') # this process creates correct CSV field types

nodeTree = nodeTemplate.to_dict('records')


with open('xWeather_Erasmus_US_250.json', "r") as file: # encoding='utf-8') as file:
    data = json.load(file)
    
events = []

for i in range(len(data)):
    events.append( data[i]['_source']['event'] )
    #print(data[i]['_source']['event'])

#remove event redundancies in list    
events = list(set(events))
events = sorted(events)
#print (str(events))

tags = []
eventTblID = 11 # assign a unique (arbitrary) table_id

nodeID = nodeList[-1]['np_node_id'] #nodes['np_node_id'][len(nodes) - 1]  #zz need to fix this
parentID = 0 # link A-end
childID = 0  # link B-end


# Loop through all events to create the node and tag tables
for i in range(len(data)):
    
    # get eventCat number
    eventCat = events.index(data[i]['_source']['event'])
    #print(data[i]['_source']['event'])
    
    tags.append( {'record_id': i+1,
                  'table_id': eventTblID,
                  'title': data[i]['_source']['event'],
                  #'description': "" } )
                  'description': data[i]['_source']['articles'][0]['article_title'] } )
      
    #for k in range(len(data[i]['_source']['articles'])):        
        #print(data[i]['_source']['articles'][k]['article_title'])
        #print()
    
    # event node (links to event location node layer)
    nodeList.append( nodeTree[rootTree].copy() )
    
    # increment id's
    nodeID += 1  
    parentID = 0        # root node's have parent_id = 0
    eventID = nodeID
    
    eventIndex = len(nodeList)
    
    # apply id's
    nodeList[-1]['np_node_id'] = nodeID
    nodeList[-1]['parent_id' ] = parentID
    
    nodeList[-1]['np_table_id'] = eventTblID
    nodeList[-1]['record_id'] = i+1 #nodeID
    
    # lat/long, unless 0,0 in which case auto-distribute
    lat = data[i]['_source']['locations'][0]['location']['lat']
    lon = data[i]['_source']['locations'][0]['location']['lon']
    
    # ascert valid lat long coords
    if lat != 0.0 or lon != 0.0:
        nodeList[-1]['translate_x'] = lon
        nodeList[-1]['translate_y'] = lat
    else:
        nodeList[-1]['translate_x'] += i * 2.0     # if invalid, auto-distribute
        nodeList[-1]['translate_y'] += i * 100.0   # north of the grid by 10 deg
        
    nodeList[-1]['translate_z'] = -10.0
    
    probA = int(data[i]['_source']['probability'] * 255)
    if probA > 255:
        probA = 255
        
    nodeList[-1]['color_a'] = probA # transparency
    
    nodeList[-1]['np_texture_id'] = eventCat + 1
    
    # event centroid
    locNum = len(data[i]['_source']['locations'])
    latAvg = 0.0
    lonAvg = 0.0 
      
    for j in range(locNum):
              
        # create event location node
        nodeList.append( nodeTree[rootTree].copy() )
       
        nodeID += 1  
        parentID = 0        # root
        L1 = nodeID
        
        # set the id's
        nodeList[-1]['np_node_id'] = nodeID
        nodeList[-1]['parent_id' ] = parentID
        
        nodeList[-1]['np_table_id'] = eventTblID
        nodeList[-1]['record_id'] = i+1 #nodeID

        # set root position to lat/long, uless 0,0 in which case auto-distribute
        lat = data[i]['_source']['locations'][j]['location']['lat']
        latAvg += lat
        lon = data[i]['_source']['locations'][j]['location']['lon']
        lonAvg += lon
        
        if lat != 0.0 or lon != 0.0:
            nodeList[-1]['translate_x'] = lon
            nodeList[-1]['translate_y'] = lat
        else:
            nodeList[-1]['translate_x'] += i * 5.0     # root trans.x offset
            
        # event specific node attributes
        nodeList[-1]['np_color_id'] = eventCat
        
        probB = int(data[i]['_source']['probability'] * 255)
        if probB > 255:
            probB = 255
            
        #print(data[i]['_source']['probability'])
        nodeList[-1]['color_a'] = probB
        
        # scale the event location glyph height based on population
        popu = data[i]['_source']['locations'][j]['population'] * 0.00002
        popu = np.sqrt(popu)
        nodeList[-1]['scale_x'] = 0.2
        nodeList[-1]['scale_y'] = 0.2
        nodeList[-1]['scale_z'] = popu
        
        # create a link node
        nodeList.append( nodeTree[rootTree].copy() )
       
        nodeID += 1  
        parentID = eventID        # root
        
        # set the id's
        nodeList[-1]['np_node_id'] = nodeID
        nodeList[-1]['parent_id' ] = parentID
        
        
        # link node
        nodeList[-1]['type' ] = 7
        nodeList[-1]['child_id' ] = nodeID - 1
        
        nodeList[-1]['np_geometry_id' ] = 3     
        nodeList[-1]['np_color_id'] = eventCat

        # needs to match tag table
        nodeList[-1]['np_table_id'] = eventTblID
        nodeList[-1]['record_id'] = i   # nodeID


    nodeList[eventIndex - 1]['translate_x'] = lonAvg / locNum
    nodeList[eventIndex - 1 ]['translate_y'] = latAvg / locNum
    
    #print( "{:3.2f}".format(nodeList[eventIndex - 1]['translate_x']))
    #print( "{:3.2f}".format(lonAvg) + " " +  str(locNum) + " " + data[i]['_source']['probability'])
    #print()


# save node table
filePath = "../csv/xWeather-Gz_np_node.csv"

print( "Save: " +  filePath )
nodes = pd.DataFrame.from_records(nodeList)
nodes.to_csv(filePath, index = False)


# method exports CSV with proper field types for our native tables
tagsDF = pd.DataFrame.from_records( tags )

filePath = "../csv/xWeather-Gz_np_tag.csv"
                
print( "Save: " +  filePath )
tagsDF.to_csv( filePath, index = False )
