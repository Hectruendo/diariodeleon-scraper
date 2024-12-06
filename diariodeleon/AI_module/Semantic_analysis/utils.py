def transform_keys(entry: dict) -> dict:
    """
    Transform keys in the dictionary to match the Noticia model requirements.

    Args:
        entry (dict): The original dictionary.

    Returns:
        dict: The transformed dictionary with renamed keys.
    """
    if "main_keywords" in entry:
        # Convert 'main_keywords' to 'keywords_openai' as a list
        entry["keywords_openai"] = entry.pop("main_keywords").split(", ")

    if "keywords" in entry:
        # Rename 'keywords' to 'keywords_diary'
        entry["keywords_diary"] = entry.pop("keywords")

    if "population_groups" in entry:
        # Convert 'population_groups' to a list
        entry["population_groups"] = entry.pop("population_groups").split(", ")

    return entry

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