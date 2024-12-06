import json
from schemas.NoticiaSchema import Noticia
from tqdm import tqdm
from utils import transform_keys
from SpanishTextEmbedder import SpanishTextEmbedder

USERNAME = "panchojasen"


path = f"/home/{USERNAME}/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias.jsonl"


# Embedder = SpanishTextEmbedder(device="cuda")

with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]

for result in tqdm(data):
    result = transform_keys(result)
    result
    noticia = Noticia(**result)
    
noticia.author