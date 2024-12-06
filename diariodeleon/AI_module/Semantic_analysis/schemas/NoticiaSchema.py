from pydantic import BaseModel, field_validator, model_validator, root_validator, validator
from typing import List, Optional, ClassVar, Dict
import sys

sys.path.append("..")
from name_synonyms import SYNONYMS as NAME_SYNONIMS
from collective_synonyms import collective_synonyms as POPULATION_SYNONIMS
# print(NAME_SYNONIMS)

class Noticia(BaseModel):
    # ID
    url: Optional[str] = None
    # Metadata
    category: Optional[str] = None
    location: Optional[str] = None
    publication_date: Optional[str] = None
    updated_date: Optional[str] = None
    keywords_diary: Optional[List[str]] = None
    image: Optional[str] = None

    author: Optional[str] = None
    author_normalized: Optional[str] = None
    # Content
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    # OpenAI Analysis
    population_groups: Optional[List[str]] = None
    population_groups_normalized: Optional[List[str]] = None
    keywords_openai: Optional[List[str]] = None
    numero_protagonistas: Optional[int] = None
    numero_protagonistas_femeninos: Optional[int] = None
    numero_protagonistas_masculinos: Optional[int] = None
    numero_sujetos_secundarios: Optional[int] = None
    numero_sujetos_secundarios_femeninos: Optional[int] = None
    numero_sujetos_secundarios_masculinos: Optional[int] = None
    # Embeddings
    title_embedding: Optional[List[float]] = None
    subtitle_embedding: Optional[List[float]] = None
    content_embedding: Optional[List[float]] = None
    keywords_diary_embedding: Optional[List[List[float]]] = None
    keywords_openai_embedding: Optional[List[List[float]]] = None
    population_groups_embedding: Optional[List[List[float]]] = None

    # Synonims
    author_synonyms_map: ClassVar[Dict[str, str]] = {}
    population_groups_synonyms_map: ClassVar[Dict[str, str]] = {}


    @root_validator(pre=True)
    def clean_empty_lists(cls, values):
        """
        Clean empty lists for specific fields before validation.
        """
        fields_to_clean = ["keywords_diary", "keywords_openai", "population_groups", "population_groups_normalized"]
        for field in fields_to_clean:
            if field in values and isinstance(values[field], list):
                values[field] = [item.strip() for item in values[field] if item.strip()]
        return values
    
    @classmethod
    def load_synonyms(cls):
        """
        Loads the canonical mapping for authors and population groups once.
        """
        # Only load if not already loaded
        if not cls.author_synonyms_map:
            cls.author_synonyms_map = cls.create_variant_to_canonical_mapping(NAME_SYNONIMS)
            print('-----------------')
            print("Author synonyms loaded:")
        if not cls.population_groups_synonyms_map:
            cls.population_groups_synonyms_map = cls.create_variant_to_canonical_mapping(POPULATION_SYNONIMS)
            print('-----------------')
            print("Population group synonyms loaded:")
    
    @staticmethod
    def create_variant_to_canonical_mapping(variants_dict):
        """
        Creates a reverse mapping from normalized variants to canonical names.
        """
        variant_to_canonical = {}
        for canonical_name, variants in variants_dict.items():
            normalized_canonical_name = canonical_name
            variant_to_canonical[normalized_canonical_name] = canonical_name
            for variant in variants:
                normalized_variant = variant
                variant_to_canonical[normalized_variant] = canonical_name
        return variant_to_canonical

    @validator("author_normalized", always = True)
    def set_author_normalized(cls, v, values):
        """
        Automatically set the `author_normalized` field based on the `author` field,
        using the `roseta` mapping for normalization.
        """
        cls.load_synonyms()  
        author = values.get("author")
        if author:
            normalized_author = cls.author_synonyms_map.get(author.strip().lower(), author.strip().lower()) 
            if normalized_author != author.strip().lower():
                print('THIS IS IT',author, normalized_author)
            return normalized_author
        return v

    @validator("population_groups_normalized", always = True)
    def set_population_groups_normalized(cls, v, values):
        """
        Automatically set the `population_groups_normalized` field based on the `population_groups` field,
        using the `roseta` mapping for normalization.
        """
        cls.load_synonyms()  
        population_groups = values.get("population_groups")
        if population_groups:
            normalized_population_groups = [
                cls.population_groups_synonyms_map.get(group.strip().lower(), group) for group in population_groups
            ]
            return normalized_population_groups
        return v
