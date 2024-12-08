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
    # Embeddings
    title_embedding: Optional[List[float]] = None
    subtitle_embedding: Optional[List[float]] = None
    content_embedding: Optional[List[float]] = None
    keywords_diary_embeddings: Optional[List[List[float]]] = None
    keywords_openai_embeddings: Optional[List[List[float]]] = None
    population_groups_embeddings: Optional[List[List[float]]] = None
    # Embedding model
    embedding_model: ClassVar = SpanishTextEmbedder()

    def calculate_embeddings(self):
        """
        Creates embeddings for title, subtitle, content, keywords_diary, keywords_openai,
        and population_groups. All text fields are embedded at once, and then the results
        are mapped back to their respective attributes.
        """

        list_to_embed = []
        # Mapping from field name to (start_index, end_index) in the `to_embed` list
        field_index_map = {}

        # Single fields: title, subtitle, content
        single_fields = [
            ("title", self.title),
            ("subtitle", self.subtitle),
        ]

        # List fields: keywords_diary, keywords_openai, population_groups
        list_fields = [
            ("keywords_diary", self.keywords_diary),
            ("keywords_openai", self.keywords_openai),
            ("population_groups", self.population_groups),
        ]

        # Collect single field texts
        current_idx = 0
        for fname, value in single_fields:
            if value is not None and value.strip():
                # Add the single text to the embedding list
                list_to_embed.append(value.strip())
                # Store the segment indices for later retrieval
                field_index_map[fname] = (current_idx, current_idx + 1)
                current_idx += 1

        # Collect list field texts
        for fname, value_list in list_fields:
            if value_list:
                # Add all values in the list to the embedding list
                cleaned = [v.strip() for v in value_list if v.strip()]
                if cleaned:
                    start = current_idx
                    list_to_embed.extend(cleaned)
                    end = current_idx + len(cleaned)
                    field_index_map[fname] = (start, end)
                    current_idx = end

        # If there's nothing to embed, just return
        if not field_index_map:
            return

        # Embed all texts at once
        embeddings = self.embedding_model.embed(list_to_embed)
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        single_field_names = [name for name, _ in single_fields]
        # Distribute embeddings back to their respective fields
        for fname, (start, end) in field_index_map.items():
            segment = embeddings[start:end]
            if fname in single_field_names:
                setattr(self, f"{fname}_embedding", segment[0])
            else:
                setattr(self, f"{fname}_embeddings", segment)

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
