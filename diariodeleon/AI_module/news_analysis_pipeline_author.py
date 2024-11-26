import json
import os

from tqdm import tqdm

from prompts import SYSTEM_MESSAGE, USER_MESSAGE
from name_synonyms import SYNONYMS
from News_Parser_Controllers import NewsParser, Prompt
from utils import modify_text_for_llm


from dotenv import load_dotenv
load_dotenv() 

article_limit = 5000
years = [2024]




def create_variant_to_canonical_mapping(variants_dict):
    """
    Creates a reverse mapping from normalized variants to canonical names.
    """
    variant_to_canonical = {}
    for canonical_name, variants in variants_dict.items():
        # Normalize the canonical name
        normalized_canonical_name = canonical_name
        # Map the normalized canonical name to itself
        variant_to_canonical[normalized_canonical_name] = canonical_name
        # Map each normalized variant to the canonical name
        for variant in variants:
            normalized_variant = variant
            variant_to_canonical[normalized_variant] = canonical_name
    return variant_to_canonical

roseta = create_variant_to_canonical_mapping(SYNONYMS)



prompt = Prompt(SYSTEM_MESSAGE.strip(), USER_MESSAGE.strip())

news_parser = NewsParser(os.environ.get("OPENAI_API_KEY"), prompt = prompt)


path = '/home/adrian.alvarez/Projects/diariodeleon-scraper/results/resultados_recientes.jsonl'
with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]

def count_authors(data_dict:dict, conversion_dict:dict):
    authors_counts = {}
    for article in data_dict:
        if 'author' not in article:
            continue
        author = article['author']
        if author in conversion_dict:
            author = conversion_dict[author]
        if author in authors_counts:
            authors_counts[author] += 1
        else:
            authors_counts[author] = 1
    return authors_counts


def count_authors_data(data_dict:dict, conversion_dict:dict):
    authors_counts = {}
    for url in data_dict:
        if 'author' in data_dict[url]:
            author = data_dict[url]['author']
            if author in conversion_dict:
                author = conversion_dict[author]
            if author in authors_counts:
                authors_counts[author] += 1
            else:
                authors_counts[author] = 1
    return authors_counts


author_counts = count_authors(data, roseta)


file_path = "/home/adrian.alvarez/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias.jsonl"
json_results = {}

# Check if the file exists, if it does, load it into `json_results`
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            article = json.loads(line)
            json_results[article['url']] = article

results_counter = count_authors_data(json_results, roseta)


authors = [
    "Pacho Rodríguez",
    "Verónica Viñas",
    "María Carnero",
    "Pilar Infiesta",
    "Álvaro Caballero",
    "Luis Urdiales",
    "Cristina Fanjul",
    "Ángel Fraguas",
    "Maria Carro",
    "Manuel Félix",
    "Ángel Fidalgo",
    "Joaquín S.Torné",
    "Maite Rabanillo",
    "Maria Jesús Muñiz",
    "Carmen Tapia",
    "Ana Gil",
    "Miguel Angel Zamora",
    "Ana Gaitero",
]

#create a counter of authors based on results_counter
authors_counter = {}
for i, key in enumerate(results_counter):
    if roseta.get(key, key) in authors:
        authors_counter[key] = {}
        authors_counter[key]['total'] = author_counts[key]

        authors_counter[key]['done'] = results_counter[key]
        authors_counter[key]['percentaje'] = results_counter[key] / author_counts[key] * 100


for article in tqdm(data):
    
    if 'publication_date' not in article or int(article['publication_date'][:4]) not in years:
        # print("Article is not from the specified year, skipping...")
        continue   
    
    if article['url'] in json_results:
        # print("Article already processed, skipping...")
        continue
    
    if 'content' not in article or len(article['content']) < 100:
        # print("Article content is too short, skipping...")
        continue
    
    author = article.get('author', None)
    author_synonym = roseta.get(author, author)
    if author_synonym not in authors:
        # print("Article author is not in the list, skipping...")
        continue
    
    if authors_counter[author_synonym]['done'] >= 90 and authors_counter[author_synonym]['percentaje'] > 30:
        # print("Author has already reached the limit, skipping...")
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

    
print("Finished processing all articles.")
    
