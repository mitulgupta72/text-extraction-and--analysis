import pandas as pd
import numpy as np
import nltk
import re
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import requests
import urllib
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import warnings
warnings.filterwarnings('ignore')
import os
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lem = WordNetLemmatizer()
nltk.data.path.append("C:\\Users\\mitul\\AppData\\Roaming\\nltk_data")
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = stopwords.words('english')

class data_ingestion:        
    
    def primary(self):
        try:
            data = pd.read_excel(os.path.join("Notebook/data","Input.xlsx"))
            #print(data.head())
            return data
        except Exception as e:
            print(f'Error {e}')
     
    def secondary(self):
        """Ingesting data from a given directory and scrape those link by using beautifulsoup and returns a dataframe"""
        data = pd.read_excel('D:\\SRC\\Notebook\\data\\Input.xlsx')
        df = data.copy()  # Create a copy to avoid modifying the original DataFrame
        updated_list = []
        No_Matching_Data = []
        Blank_link = {}
        
        for i, url in enumerate(df['URL']):
            response_code = requests.get(url) # creates an HTTP GET request to the specified URL
            soup = bs(response_code.text, 'html.parser') #Contains HTML contents  
            article_title = soup.find('title').text # to find the title tag
            
            all_text_element = soup.find("div", class_="td-post-content tagdiv-type") #BeautifulSoup to find a <div> element with a specific class attribute within the parsed HTML content.

            if all_text_element is not None: # Conditional Statement if data is extracted by this specify div or not
                all_text = all_text_element.get_text(strip=True, separator='\n') # If this element contain a text then those text saved in all text variables
                firstdata = all_text.splitlines() # In above code separator is used so now we split each lines
            else:
                print(f"No matching element found in the HTML for URL: {url}") # If no any text in this div element then this url along with url_id store in blank dictionary
                firstdata = []        
                Blank_link[f"blackassign00{i+1}"] = url        
                Blank = {
                        'URL_ID' : f"blackassign00{i+1}" ,
                        'URL'    : url 
                        }
                No_Matching_Data.append(Blank)
                
            # new dataframe store all the extracted text 
            new_dataframe = {
                    "URL_ID": df["URL_ID"][i],
                    'URL' : url,
                    'article_words':f"{article_title}-{firstdata}"
                }    
            
            updated_list.append(new_dataframe)

            filename = urllib.parse.quote_plus(url) # this will convert the url as url name for the text file
            file_path = 'D:\\SRC\\Text_files' #Path to store text files
            space = " "
                
            with open(f"{file_path}\{filename}.txt", 'w+',encoding='utf-8') as file1: #Creating text files by there names and inserting article title and text
                file1.writelines(article_title)
                file1.writelines(space)
                if firstdata is None:
                    firstdata = 'No data found'
                else:
                    file1.writelines(firstdata)
        return pd.DataFrame(updated_list),No_Matching_Data # Returns dataframe 
    
    
    def Handdle_Blank_link(self,blank_data): # same as above method but this method is used for extracting those text which are not extracted by secondary method
        updated_list = []
        
        for item in blank_data:
            i = item['URL_ID']
            j = item['URL']
            response_code = requests.get(j)
            soup = bs(response_code.text, 'html.parser')
            article_title = soup.find('title').text
            alldiv = soup.find("div", class_="td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type")
            if alldiv is not None:
                firstdata = alldiv.text
                filename = urllib.parse.quote_plus(j)
                file_path = 'D:\\SRC\\Text_files'
                space = " "                
                with open(f"{file_path}\\{filename}.txt", 'w+') as file1:
                    file1.writelines(article_title)
                    file1.writelines(space)
                    file1.writelines(firstdata)             
                updated_dict = {
                    'URL_ID': i,
                    'URL': j,
                    'article_words': f"{article_title} - {firstdata}"
                }
                updated_list.append(updated_dict)
            else:
                print(f"No data available for the link: {j}")
        df = pd.DataFrame(updated_list)
        return df #return a dataframe 

    def merged(self,df1,df2): #
        merged_df = pd.merge(df1, df2, on=['URL_ID', 'URL'], how='left') #merged both dataframe and store in this variable
        merged_df = merged_df.dropna()
        merged_df.reset_index(drop=True, inplace=True)
        merged_df.to_csv('D:\\SRC\\Notebook\\data\\final.csv', index=False) # dataframe is saved in csv format
        return merged_df