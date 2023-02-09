from selenium import webdriver
import time
import json
import pandas as pd
from selenium.webdriver.common.by import By
import regex as re
import os
import webscrape_yelp as wbs
from csv import writer
from datetime import date

# intitiate search criteria
search_term = "Hair Stylist"
num_of_page = 10
state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
search_states = [re.sub(" ", "+", x) for x in state_names]
save_dir = os.path.join(os.getcwd() + 'data')
combine_state_files = False

# Create a dictionary of all business links to scrape reviews from
all_biz_links = {}
for state in search_states:
    print('Searching {} for {} Businesses'.format(state,search_term))
    all_biz_links[state] = wbs.getBizLinks(num_of_page, state, search_term)
all_biz_df = pd.DataFrame(all_biz_links.items(), columns=['state', 'biz_dict'])
all_biz_df.to_csv(os.path.join(save_dir, 'all_biz_links.csv'))

# Initiate bizs df
if os.path.exists(save_dir, 'bizs.csv'):
    bizs = pd.read_csv(os.path.join(save_dir, 'bizs.csv'))
    biz_id = bizs['biz_id'].max() + 1
else:
    bizs = pd.DataFrame()
    biz_id = 0

# In case of interruption - record all reviews_*.csv files in the save_dir
# Save remaining states in a new list
cur_save_states = []
for filename in os.listdir(save_dir):
    if filename.startswith('reviews_'):
        x = re.split('_', filename,2)[1]
        y = re.split(r'\.', x ,2)[0]
        cur_save_states.append(y)
rem_states = [x for x in list(all_biz_links) if x not in cur_save_states]

# Run through all states need reviews for. Save a new file for each state and the unique list of biz
for state in rem_states:
    print(state)
    r_state = pd.DataFrame()
    for link in list(all_biz_links[state]):
        biz_id = biz_id + 1
        r,b = wbs.getData(biz_id, link)
        r_state = r_state.append(r)
        bizs = bizs.append(b)
    r_state.to_csv(os.path.join(save_dir, 'reviews_{}.csv'.format(state)))
    bizs.to_csv(os.path.join(save_dir, 'bizs.csv')) # this will write over the bizs file. but a better method is needed for optimization

# Combined file
if combine_state_files == True:
    reviews_tmp = []
    for filename in os.listdir():
        if filename.startswith('reviews'):
            reviews_state = pd.read_csv(filename).iloc[:,1:]
            #print(len(reviews_state), filename)
            reviews_tmp.append(reviews_state)
    reviews_df = pd.concat(reviews_tmp)
    reviews_df.index.names = ['review_id']
    reviews_df.to_csv('all_reviews_{}.csv'.format(date.today().strftime("%Y%m%d")))
