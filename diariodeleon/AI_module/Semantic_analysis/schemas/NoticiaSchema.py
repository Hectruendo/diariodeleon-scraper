from pydantic import BaseModel, root_validator, validator
from typing import List, Optional, ClassVar, Dict
import sys
import numpy as np

sys.path.append("..")
from name_synonyms import SYNONYMS as NAME_SYNONIMS
from collective_synonyms import collective_synonyms as POPULATION_SYNONIMS

from SpanishTextEmbedder import SpanishTextEmbedder


class NoticiaBase(BaseModel):
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

class NoticiaEmbeddings(NoticiaBase):
    embedding_model: ClassVar = SpanishTextEmbedder()
    # Define which fields to embed, and whether they are single or multiple
    fields_to_embed: ClassVar = {
        "title": {"multiple": False, "enabled": True},
        "subtitle": {"multiple": False, "enabled": True},
        "keywords_diary": {"multiple": True, "enabled": True},
        "keywords_openai": {"multiple": True, "enabled": True},
        "population_groups": {"multiple": True, "enabled": True},
    }
    
    title_embedding: Optional[List[float]] = None
    subtitle_embedding: Optional[List[float]] = None
    content_embedding: Optional[List[float]] = None
    keywords_diary_embeddings: Optional[List[List[float]]] = None
    keywords_openai_embeddings: Optional[List[List[float]]] = None
    population_groups_embeddings: Optional[List[List[float]]] = None

    def calculate_embeddings(self):
        list_to_embed = []
        field_index_map = {}

        # Iterate over the configuration rather than hardcoding fields
        current_idx = 0
        for field_name, config in self.fields_to_embed.items():
            if not config["enabled"]:
                continue  # Skip embedding this field entirely if disabled

            value = getattr(self, field_name, None)
            if value is None:
                continue  # If the field is None, skip embedding
            
            if config["multiple"] and isinstance(value, list):
                # Clean and filter out empty entries
                cleaned = [v.strip() for v in value if v and v.strip()]
                if cleaned:
                    start = current_idx
                    list_to_embed.extend(cleaned)
                    end = current_idx + len(cleaned)
                    field_index_map[field_name] = (start, end)
                    current_idx = end
            else:
                # Single-field embedding
                text = value.strip()
                if text:
                    list_to_embed.append(text)
                    field_index_map[field_name] = (current_idx, current_idx + 1)
                    current_idx += 1

        if not field_index_map:
            return  # Nothing to embed

        embeddings = self.embedding_model.embed(list_to_embed)
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()

        # Assign embeddings back to the model fields
        for field_name, (start, end) in field_index_map.items():
            segment = embeddings[start:end]
            if self.fields_to_embed[field_name]["multiple"]:
                setattr(self, f"{field_name}_embeddings", segment)
            else:
                setattr(self, f"{field_name}_embedding", segment[0] if segment else None)

    def calculate_embeddings_main_content(self):
        if self.content:
            self.content_embedding = self.embedding_model.embed([self.content[:8193]])[0].tolist()

    def model_post_init(self, __context):
        self.calculate_embeddings()
        self.calculate_embeddings_main_content()


class Noticia(NoticiaEmbeddings):
    # Class variables to store the synonyms mapping
    # Synonims for authors
    author_synonyms_map: ClassVar[Dict[str, str]] = {}
    population_groups_synonyms_map: ClassVar[Dict[str, str]] = {}

    @root_validator(pre=True)
    def clean_empty_values(cls, values):
        """
        1. Clean empty lists for specific fields by removing empty items.
        2. Convert empty string values to None for specified fields.
        """
        fields_to_clean_lists = [
            "keywords_diary",
            "keywords_openai",
            "population_groups",
            "population_groups_normalized",
        ]
        fields_to_clean_strings = [
            "url",
            "category",
            "location",
            "publication_date",
            "updated_date",
            "author",
            "author_normalized",
            "title",
            "subtitle",
            "content",
        ]

        # Clean list fields by stripping items and removing empties
        for field in fields_to_clean_lists:
            if field in values and isinstance(values[field], list):
                values[field] = [item.strip() for item in values[field] if item.strip()]

        # Convert empty strings to None for specified string fields
        for field in fields_to_clean_strings:
            if field in values and isinstance(values[field], str):
                if values[field].strip() == "" or values[field].strip().lower() == "null":
                    values[field] = None

        return values

    @classmethod
    def load_synonyms(cls):
        """
        Loads the canonical mapping for authors and population groups once.
        """
        # Only load if not already loaded
        if not cls.author_synonyms_map:
            cls.author_synonyms_map = cls.create_variant_to_canonical_mapping(NAME_SYNONIMS)
            print("-----------------")
            print("Author synonyms loaded:")
        if not cls.population_groups_synonyms_map:
            cls.population_groups_synonyms_map = cls.create_variant_to_canonical_mapping(POPULATION_SYNONIMS)
            print("-----------------")
            print("Population group synonyms loaded:")

    @staticmethod
    def create_variant_to_canonical_mapping(variants_dict: Dict[str, List[str]], to_lower: bool = True):
        """
        Creates a reverse mapping from normalized variants to canonical names.
        If to_lower is True, the keys will be stored in lowercase.
        """
        variant_to_canonical = {}
        for canonical_name, variants in variants_dict.items():
            normalized_canonical_name = canonical_name.lower() if to_lower else canonical_name
            variant_to_canonical[normalized_canonical_name] = canonical_name
            for variant in variants:
                normalized_variant = variant.lower() if to_lower else variant
                variant_to_canonical[normalized_variant] = canonical_name
        return variant_to_canonical

    @validator("author_normalized", always=True)
    def set_author_normalized(cls, v, values):
        """
        Automatically set the `author_normalized` field based on the `author` field,
        using the `roseta` mapping for normalization.
        """
        cls.load_synonyms()
        author = values.get("author")
        if author:
            normalized_author = cls.author_synonyms_map.get(author.strip().lower(), author.strip().lower())
            return normalized_author
        return v

    @validator("population_groups_normalized", always=True)
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
