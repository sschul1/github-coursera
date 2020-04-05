#!/usr/bin/env python
# coding: utf-8

# In[15]:


#Import & Installation
import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

get_ipython().system('conda install -c conda-forge geopy --yes ')
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes ')
import folium # map rendering library

from bs4 import BeautifulSoup


print('Libraries imported.')


# # Capstone Project - The Battle of Neighborhoods (Week 1 & Week 2)
This notebook contains the solution of the whole Capstone Project (Week 1&2)
The tasks were the following:

First week:
"A description of the problem and a discussion of the background."
"A description of the data and how it will be used to solve the problem."

Second week:
"A link to your Notebook on your Github repository, showing your code."
"A full report consisting of all of the following components."

(!) Note: In this notebook I remain in the use of "we" - This refers only to the case - This notebook was not created in cooperation, but by me.
# # 1 Introduction and Discussion of the Business Objective and Problem
Our team is part of a start-up spin-off of a luxury fashion brand. The new brand should act as a luxurious counterpart to the rather conservative line of the house. 

The new brand is already successful in the online segment and we sell our products through the most popular trend shops. This success is to be used and converted into a new store concept. The Pop-Up Store is to be held in Manhattan. 

New York City is the American centre of fashion and the whole world is a guest there. Especially during Fashion Week, the whole elite of the industry moves to New York City.

Our market research department has already found out that the intended store concept - a fusion of café, event location and shop - is very well accepted by the target group. The latter, in turn, has a particularly high household income and they are mainly moving to areas where there are many cafés, coffee shops, restaurants and clothing stores. The target group avoids long distances. 
The task now is to find suitable locations in Manhattan. Foursquare data will be very helpful in making data-driven decisions about the best of those areas.
# # 2 Specific Criteria & the Data Flow
The data of our market research team strongly suggests that the best places are in fact areas that are near Japanese Restaurants, Cafés and Wine Bars and other Clothing Stores. Moreover our target group seems to be indifferent if other luxury retailer are nearby or not, because a lot of them are living an alternative way of live. The social aspect is much more important.

To optimize the search we deviate from the classical way and use the available data. 
Unstructured searches are avoided. This reduces the search costs and the personal preferences of the employees do not distort the already defined selection criteria.

Moreover it is important to say, that the final figures are used as an indicator: The final decision is made on site by the head of department. 

This outlined data process goes through several steps:
1.) We use the available geo data of New York City and enrich them with information about the venues of Foursquare.
2.) In the next step we analyze the data by the defined criteria.
3.) Thereafter we visualize our results.
4.) Finally, we summarize the results and make a recommendation for action.

Technically, we use the following points:
- Reading data
- Use of an API (Foursquare)
- Data connection and selection 
- Aggregation of the data level 
- Visualization
# In[16]:


# After you know more about the Business Case and after importing the required libraries, in this cell a download will be executed
# The file contains information about the 5 boroughs and the neighborhoods of NYC
get_ipython().system("wget -q -O 'newyork_data.json' https://cocl.us/new_york_dataset")
print('Data downloaded!')


# In[8]:


import json


# In[17]:



with open('newyork_data.json') as json_data:
    newyork_data = json.load(json_data)


# In[18]:


newyork_data


# In[19]:


neighborhoods_data = newyork_data['features']


# In[20]:


neighborhoods_data[0]


# In[21]:


# define the dataframe columns
column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 

# instantiate the dataframe
neighborhoods = pd.DataFrame(columns=column_names)


# In[22]:


neighborhoods


# In[23]:


for data in neighborhoods_data:
    borough = neighborhood_name = data['properties']['borough'] 
    neighborhood_name = data['properties']['name']
        
    neighborhood_latlon = data['geometry']['coordinates']
    neighborhood_lat = neighborhood_latlon[1]
    neighborhood_lon = neighborhood_latlon[0]
    
    neighborhoods = neighborhoods.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)


# In[24]:


neighborhoods.head()

Instead of looking at all the NYC data, as in the lab, we'll skipt htis here and focus on Manhattan. 
# In[25]:


manhattan_data = neighborhoods[neighborhoods['Borough'] == 'Manhattan'].reset_index(drop=True)
manhattan_data.head()


# In[26]:


address = 'Manhattan, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Manhattan are {}, {}.'.format(latitude, longitude))


# In[27]:


# create map of Manhattan using latitude and longitude values
map_manhattan = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(manhattan_data['Latitude'], manhattan_data['Longitude'], manhattan_data['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_manhattan)  
    
map_manhattan

We now have the relevant geographic information on Manhattan and the neighborhoods. These can be viewed on the map. The Foursquare Api is now used to get the necessary information about the neighborhoods of Manhattan.

(!) Please notice, that I will not upload my personal Foursquare data. So you have to insert your own CLIENT_ID and CLIENT_SECRET.
# In[28]:


CLIENT_ID = 'XXX' 
CLIENT_SECRET = 'YYY'
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[31]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    LIMIT=100
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[32]:


manhattan_venues = getNearbyVenues(names=manhattan_data['Neighborhood'],
                                   latitudes=manhattan_data['Latitude'],
                                   longitudes=manhattan_data['Longitude']
                                  )


# In[34]:


print(manhattan_venues.shape)
manhattan_venues.head(105)


# In[35]:


manhattan_venues.groupby('Neighborhood').count()


# # Analyze the Neighborhoods
Now begins the part where we analyze the data and compare the partial results with the requirements we have already defined
# In[36]:


# We start with looking for the top venues in each neighborhood (like in the lab)


# In[37]:


# one hot encoding
manhattan_onehot = pd.get_dummies(manhattan_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
manhattan_onehot['Neighborhood'] = manhattan_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [manhattan_onehot.columns[-1]] + list(manhattan_onehot.columns[:-1])
manhattan_onehot = manhattan_onehot[fixed_columns]

manhattan_onehot.head()


# In[38]:


manhattan_grouped = manhattan_onehot.groupby('Neighborhood').mean().reset_index()
manhattan_grouped


# In[41]:


num_top_venues = 5

for hood in manhattan_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = manhattan_grouped[manhattan_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[42]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[43]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = manhattan_grouped['Neighborhood']

for ind in np.arange(manhattan_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(manhattan_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# # Analyzing by Visualization
Data that have been graphically processed are often easier to understand and convey their message better. That is why we, as a department of the brand, have decided to use a graphic for analysis at this point. 

More precisely, it is a violin plot that has already been used for similar questions and generates good insights. 
On the X-axis are the names of the neighborhoods of Manhattan. On the Y-axis the frequency is plotted. The height and width of the graphics per neighborhood represent the frequency. 

The graphics are displayed one below the other. One line represents one of the selection criteria. 
Only potential locations that have a frequency in all criteria are considered. 

As a reminder, these were:
- Japanese Restaruant
- Café
- Wine bar
- Clothing Stores

# In[49]:


import seaborn as sns
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(50,25))
sns.set(font_scale=1.1)

ax = plt.subplot(4,1,1)
sns.violinplot(x="Neighborhood", y="Japanese Restaurant", data=manhattan_onehot, cut=0);
plt.xlabel("")

ax = plt.subplot(4,1,2)
sns.violinplot(x="Neighborhood", y="Café", data=manhattan_onehot, cut=0);
plt.xlabel("")

plt.subplot(4,1,3)
sns.violinplot(x="Neighborhood", y="Wine Bar", data=manhattan_onehot, cut=0);

plt.subplot(4,1,4)
sns.violinplot(x="Neighborhood", y="Clothing Store", data=manhattan_onehot, cut=0);

ax.text(-1.0, 3.1, 'Frequency distribution for the top venue categories for each neighborhood', fontsize=60)
plt.savefig ("Distribution_Frequency_Venues_categories_clothing_Manhattan.png", dpi=240)
plt.show()

As can be seen in the diagram, there are some overlaps and therefore some options for the new store in Manhattan:
- Lenox Hill
- Little Italy
- Soho
- Carnegie Hill
- Midtown SouthFinally, we visualize the results by creating a new data frame in the notebook with the local data of the relevant neighborhoods. 
For this purpose, 5 small data frames are created, which are finally assembled in a new one. 

At the end you can see a map with the 5 potential points / neighborhoods.
# In[74]:


df1 = manhattan_data[manhattan_data['Neighborhood'] == 'Lenox Hill']
df2 = manhattan_data[manhattan_data['Neighborhood'] == 'Little Italy']
df3 = manhattan_data[manhattan_data['Neighborhood'] == 'Soho']
df4 = manhattan_data[manhattan_data['Neighborhood'] == 'Carnegie Hill']
df5 = manhattan_data[manhattan_data['Neighborhood'] == 'Midtown South']
df = df1.append([df2, df3, df4, df5], ignore_index=True)


# In[75]:


df.head()


# In[78]:


# create map of Manhattan using latitude and longitude values
map_manhattan_final = folium.Map(location=[latitude, longitude], zoom_start=12)

# add markers to map
for lat, lng, label in zip(df['Latitude'], df['Longitude'], df['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_manhattan_final)  
    
map_manhattan_final


# # Results, Discussion & Conclusion
Anyone who knows Manhattan will not be surprised by the findings of this investigation. 
The Neighborhoods we got as a result are very well known and trendy in terms of the luxury target group

But in the end, we have achieved a lot through this investigation:

If we had simply suspected which locations would be advantageous for the store, these would only be hypotheses and there would be a great risk of being wrong. Such mistakes may not seem bad, but in the economic world, wrong decisions can cost a lot of money and, in the worst case, threaten the very existence of a company.

In addition, we have not only narrowed down the potential locations, but we also have more information regarding the frequency of our selection criteria within the locations. This analysis alone may not be sufficient for the decision, but it is the foundation of further analysis and defines the next steps. This allows us to see afterwards which other stores are already in the neighborhoods or which restaurants and cafés might be possible cooperation partners. 

These actions or tasks are now limited by the findings of the Manhattan analysis. Thus, it is an important building block for the decision and at the same time the foundation of a structured location selection. The information could now be fed back to the market research department, which could then conduct more small-scale surveys in the neighborhoods.

Thank you very much for reading. 
Best regards
