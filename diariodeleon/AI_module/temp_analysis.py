
import json

#Open a jsonl object

path = '/home/adrian.alvarez/Projects/diariodeleon-scraper/results/resultados_recientes.jsonl'
with open(path) as f:
    data = f.readlines()
# give a python dict
data = [json.loads(line) for line in data]
#store all the values for publication_date
publication_date = []
for i in data:
    try:
        publication_date.append(i['publication_date'])
    except:
        continue

#from this get the year
year = []
for i in publication_date:
    year.append(i[:4])
set(year)
#count the number of items that are within 2024-2014
count = 0
for i in year:
    if int(i) >= 2014 and int(i) <= 2024:
        count += 1
#count per year:
count_per_year = {}
for i in year:
    if i in count_per_year:
        count_per_year[i] += 1
    else:
        count_per_year[i] = 1