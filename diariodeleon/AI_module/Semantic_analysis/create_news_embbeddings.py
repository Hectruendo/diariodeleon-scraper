import json
from schemas.NoticiaSchema import Noticia
from tqdm import tqdm
from utils import transform_keys

USERNAME = "panchojasen"


path = f"/home/{USERNAME}/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias.jsonl"

output_path = (
    f"/home/{USERNAME}/Projects/diariodeleon-scraper/results/gpt4o_row_results/analisis_noticias_embeddings.jsonl"
)

# Embedder = SpanishTextEmbedder(device="cuda")

with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]


with open(output_path, "w") as out_f:

    for n,result in enumerate(tqdm(data)):
        # if n < 1550:
        #     continue
        result = transform_keys(result)

        noticia = Noticia(**result)
        noticia_dict = noticia.model_dump()

        out_f.write(json.dumps(noticia_dict) + "\n")
        

noticias_list = []

# Read the file and load each line as a dictionary
with open(output_path, "r") as in_f:
    for line in in_f:
        if line.strip():  # Ensure to skip empty lines
            noticias_list.append(json.loads(line.strip()))
            break

noticias_list[0]