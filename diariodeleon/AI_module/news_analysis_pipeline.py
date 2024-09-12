
import json
import os

from tqdm import tqdm

from prompts import SYSTEM_MESSAGE, USER_MESSAGE
from News_Parser_Controllers import NewsParser, Prompt
from utils import modify_text_for_llm


from dotenv import load_dotenv
load_dotenv() 

prompt = Prompt(SYSTEM_MESSAGE.strip(), USER_MESSAGE.strip())

news_parser = NewsParser(os.environ.get("OPENAI_API_KEY"), prompt = prompt)


path = '/home/adrian.alvarez/Projects/diariodeleon-scraper/results/resultados_recientes.jsonl'
with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]

file_path = "/home/adrian.alvarez/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias.jsonl"
json_results = {}

# Check if the file exists, if it does, load it into `json_results`
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            article = json.loads(line)
            json_results[article['url']] = article
counter = 0
for article in tqdm(data):
    counter += 1
    if counter > 5000:
        break
    
    if article['url'] in json_results:
        print("Article already processed, skipping...")
        continue
    if 'content' not in article or len(article['content']) < 100:
        print("Article content is too short, skipping...")
        continue
    
    article_body = article['content']
    article_title = article['title']
    article_subtitle = article['subtitle']
    
    article_text = modify_text_for_llm(article_title, article_subtitle, article_body)
    
    response = news_parser.analize_news(article_text)
    article.update(response)
    # Save dict to JSON file with the name based on the URL
    json_results[article['url']] = article
     # Save just the last processed article to JSONL file
    with open(file_path, 'a') as f:
        json.dump(article, f)
        f.write('\n')
    
print("Finished processing all articles.")
    
