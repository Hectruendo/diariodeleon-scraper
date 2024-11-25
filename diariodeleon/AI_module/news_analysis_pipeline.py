import json
import os

from tqdm import tqdm

from prompts import SYSTEM_MESSAGE, USER_MESSAGE
from News_Parser_Controllers import NewsParser, Prompt
from utils import modify_text_for_llm


from dotenv import load_dotenv
load_dotenv() 

article_limit = 5000
years = [2024]



prompt = Prompt(SYSTEM_MESSAGE.strip(), USER_MESSAGE.strip())

news_parser = NewsParser(os.environ.get("OPENAI_API_KEY"), prompt = prompt)


path = '/home/adrian.alvarez/Projects/diariodeleon-scraper/results/resultados_recientes.jsonl'
with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]

def count_categories(data_dict:dict):
    category_counts = {}
    for article in data_dict:
        if 'category' not in article:
            continue
        category = article['category']
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    return category_counts

def count_categories_data(data_dict:dict):
    couter ={}
    for url in data_dict:
        if 'category' in data_dict[url]:
            if data_dict[url]['category'] in couter:
                couter[data_dict[url]['category']] += 1
            else:
                couter[data_dict[url]['category']] = 1
    return couter


def count_authors(data_dict:dict):
    authors_counts = {}
    for article in data_dict:
        if 'author' not in article:
            continue
        author = article['author']
        if author in authors_counts:
            authors_counts[author] += 1
        else:
            authors_counts[author] = 1
    return authors_counts

category_counts = count_categories(data)

author_counts = count_authors(data)

for i, key in enumerate(author_counts):
    if i > 1000:
        print(key, author_counts[key])


categories = {key : 0 for key in category_counts.keys() if category_counts[key] > 700}
categories.update({'Gente y estilo': 0})

file_path = "/home/adrian.alvarez/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias.jsonl"
json_results = {}

# Check if the file exists, if it does, load it into `json_results`
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            article = json.loads(line)
            json_results[article['url']] = article

results_counter = count_categories_data(json_results)
counter = 0

for article in tqdm(data):
    
    if 'publication_date' not in article or int(article['publication_date'][:4]) not in years:
        print("Article is not from the specified year, skipping...")
        continue   
    
    if article['url'] in json_results:
        print("Article already processed, skipping...")
        continue
    
    if 'content' not in article or len(article['content']) < 100:
        print("Article content is too short, skipping...")
        continue
    
    if 'category' not in article or article['category'] not in categories:
        print("Article category is not in the selected categories, skipping...")
        continue
    
    if article['category'] in results_counter and results_counter[article['category']] > 1000:
        print("Category already has 1500 articles, skipping...")
        continue
    
    article_body = article['content']
    article_title = article['title']
    article_subtitle = article['subtitle']
    
    article_text = modify_text_for_llm(article_title, article_subtitle, article_body)
    
    response = news_parser.analize_news(article_text)
    article.update(response)
    # Save dict to JSON file with the name based on the URL
    json_results[article['url']] = article
    #  # Save just the last processed article to JSONL file
    with open(file_path, 'a') as f:
        json.dump(article, f)
        f.write('\n')
    #count the cathegorie results
    if article['category'] in results_counter:
        results_counter[article['category']] += 1
    else:
        results_counter[article['category']] = 1
    
print("Finished processing all articles.")
    
