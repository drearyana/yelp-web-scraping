# Code for scraping data in csv file.

from selenium import webdriver
import time
import json
import pandas as pd
from selenium.webdriver.common.by import By
import regex as re

# Function for getting business links using state and search term
def getBizLinks(num_of_page, state, search_term):
    executable_path = r"C:\Users\andre\Downloads\chromedriver_win32\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=executable_path)
    driver.implicitly_wait(10)

    s = re.sub(" ", "+", search_term)
    link_get = "https://www.yelp.com/search?find_desc={}&find_loc={}&attrs=job_hair_styling&sortby=review_count".format(s, state)
    driver.get(link_get)
    time.sleep(5)
    # define a dictionary to store all cafe links and names.
    biz_dict = {}

    for page in range(num_of_page):             

        biz_name = driver.find_elements(By.XPATH, "//a[@class='css-1m051bw'][starts-with(@href, '/biz/')]")

        #Get biz names on one page
        for selenium in biz_name:
            if not selenium.text =="more":
                biz_dict[selenium.get_attribute('href')] = selenium.text

        # Get a link to next page and click the link, then delay for 5 seconds for page loading.      
        try:                         
            next_page = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
            next_page.click()
            time.sleep(10)
        except:
            print (" Check your internet speed, Cannot Click to Next page, Stop scaping restaurant link")
        
    driver.quit()

    return biz_dict

# Function to Scrape reviews data from a business link. Input a unique business ID
def getData(biz_id, link):

    biz_data_list = []
    review_data_list = []

    executable_path = r"C:\Users\andre\Downloads\chromedriver_win32\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=executable_path)
    driver.implicitly_wait(10)
    driver.get(link)
    time.sleep(5)

    # Loop each review page.   
    while True:
        try:
            page_json = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
            for selenium in page_json:
                element_json = json.loads(selenium.get_attribute("innerHTML"))
                if 'review' in element_json:
                    biz_name = element_json["name"]
                    biz_region = element_json["address"]["addressRegion"]
                    biz_avg_rating = element_json["aggregateRating"]["ratingValue"]
                    biz_review_count = element_json["aggregateRating"]["reviewCount"]
                    
                    biz_data_list.append((biz_id, biz_name, biz_region, biz_avg_rating, biz_review_count))

                    # review data list
                    for r in range(len(element_json["review"])):
                        author = element_json["review"][r]["author"]
                        datePublished = element_json["review"][r]["datePublished"]
                        reviewRating = element_json["review"][r]["reviewRating"]["ratingValue"]
                        description = element_json["review"][r]["description"]
                        review_data_list.append((author, datePublished, reviewRating, description, biz_id))                
        except:                
            print ("Check your internet speed, Error on this review page occurs, Skip the page")
               
        try:                         
            next_page = driver.find_element(By.XPATH, "//div[starts-with(@class='navigation-button-container')]")
            next_page.click()
            time.sleep(10)
        except:
            break

    review_columns = ['author', 'datePublished', 'reviewRating', 'description', 'biz_id']
    review_df = pd.DataFrame(review_data_list, columns = review_columns)
    
    biz_columns = ['biz_id', 'biz_name', 'biz_region', 'biz_avg_rating', 'biz_review_count']
    biz_df = pd.DataFrame(biz_data_list, columns=biz_columns)
    # Close Firefox browser
    driver.quit()

    return(review_df, biz_df)
    