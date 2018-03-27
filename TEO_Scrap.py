
# coding: utf-8

# In[7]:

# Install and import required packages
get_ipython().system('pip install requests')
get_ipython().system('pip install beautifulsoup4')
get_ipython().system('pip install psycopg2')

import requests
from bs4 import BeautifulSoup
import psycopg2 as pg2
from collections import Counter

# BLOG SCRAPER
# 1. Get all post links (53links)
page1 = requests.get('https://teonite.com/blog/page/1')
page2 = requests.get('https://teonite.com/blog/page/2')
page3 = requests.get('https://teonite.com/blog/page/3')
soup1 = BeautifulSoup((page1.text), 'html.parser')
soup2 = BeautifulSoup((page2.text), 'html.parser')
soup3 = BeautifulSoup((page3.text), 'html.parser')

links = (soup1.find_all('h2', attrs={'class':'post-title'})) + (soup2.find_all('h2', attrs={'class':'post-title'})) + (soup3.find_all('h2', attrs={'class':'post-title'}))
link_list = []
for link in links:
    url = link.find('a')['href']
    link_list.append('https://teonite.com' + (url))

# 2. Scrap required data from posts
# 2.1. Authors
authors = []
for link in link_list:
    article = requests.get(link)
    soup = BeautifulSoup((article.text), 'html.parser')
    author = soup.find('span', attrs={'class':'author-content'}).h4.text
    authors.append((author))
# Little data cleaning
authors = [i.strip() for i in authors]
authors = [i.replace('\n',' ') for i in authors]

# 2.2. Post contents
contents = []
for link in link_list:
    article = requests.get(link)
    soup = BeautifulSoup((article.text), 'html.parser')
    content = soup.find('section', attrs={'class':'post-content'}).text
    contents.append((content))
# Little data cleaning
contents = [i.strip() for i in contents]
contents = [content.replace('\n',' ') for content in contents]

# 2.3. Bundle scrapped information for database
blog_contents = tuple(zip(authors, contents))

# POSTGRESQL CONNECTION
# 1. Connect to local database using psycopg2
connect = pg2.connect(database='Teotest', user='postgres', password='MsrSql')
cursor = connect.cursor()

# 2. Insert scrapped data
add_blog_contents = ','.join(['%s'] * len(blog_contents))
insert_query = 'insert into blog_posts (author, post) values {}'.format(add_blog_contents)
cursor.execute(insert_query, blog_contents)
connect.commit()

# CHECK TOP 10 POPULAR WORDS
contents_split = [i.split() for i in contents]
flat_contents_split = [item for sublist in contents_split for item in sublist]
counter_contents = Counter(flat_contents_split)
top_ten = counter_contents.most_common(10)
print(top_ten)

