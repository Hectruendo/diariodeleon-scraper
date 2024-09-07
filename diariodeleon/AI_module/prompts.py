MAIN_PROMPT = """
#Instrucciones
Crea un objeto JSON que siga este esquema para analizar el contenido de una noticia.

{
  "numero_protagonistas": "Número total de personajes protagonistas sobre los que versa esta noticia. Incluye solo aquellos personajes en los que el artículo se centra principalmente, excluyendo cualquier mención secundaria.",
  "numero_protagonistas_femeninos": "Numero de protagonistas femeninos identificados en el artículo de noticias.",
  "numero_protagonistas_masculinos": "Numero de protagonistas masculinos identificados en el artículo de noticias.",
  "numero_sujetos_secundarios": 'sujetos mencionados secundariamente en la noticia, pero sobre los que no trata directamente la noticia.',
  "numero_sujetos_secundarios_femeninos": 'el numero de sujetos femeninos secundarios mencionados en la noticia',
  "numero_sujetos_secundarios_masculinos" : 'el numero de sujetos masculinos secundarios mencionados en la noticia',
  "main_keywords": "Lista de palabras clave representativas que encapsulan los elementos temáticos del artículo de noticias. No incluyas nombres propios. Da un máximo de 3, separadas por comas.",
  "population_groups": "Enumera cualquier colectivo específico mencionado como el enfoque del artículo de noticias. Da un máximo de dos, separados por comas. Ejemplos incluyen migrantes, personas con condiciones de salud mental, ancianos, veteranos.",
}

Asegúrate de no cometer errores y devuelve exclusivamente el JSON. Un intérprete de Python procesará la respuesta.


#Noticia:
{text}
#Objecto JSON:
"""