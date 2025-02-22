"""Loads in the data necessary to label and name Wikipedia entities with our taxonomy
"""
import polars as pl
from typing import Dict, Union
import json


def get_taxonomy(alg: str = "cooccurrence") -> pl.DataFrame:
    """Loads a taxonomy table from the data folder (downloaded from https://nesta-open-data.s3.eu-west-2.amazonaws.com/innovation_taxonomy/) generated using the specified algorithm.

    Args:
        alg (str, optional): algorithm used to generate the taxonomy. Defaults to "cooccurrence" - the taxonomy we found most useful based on the process described in the Medium article. Other options are "centroids" and "imbalanced" to load the taxonomies generated using the other algorithms described.

    Returns:
        pl.DataFrame: polars dataframe containing the entire taxonomy. The taxonomy is nested, and the nesting structure is represented using "_". The top level ("Level_1") is represented as a single integer (cast as a string) (ex: '0'). All of the groups at the next level within group 0 would be represented as '0_1', '0_2', '0_3', etc.

        In many cases a grouping did not break down into all 5 levels (as described in the article). In this case, the previous level is cascaded throughout the taxonomy.

        The columns in the dataframe are:
            Level_1: "disciplines" - represented by a single integer (cast as string) (ex: '0').
            Level_2: "domains" - represented by up to two integers separated by _ (cast as string) (ex: '0_1')
            Level_3: "areas" - represented by up to three integers separated by _ (cast as string) (ex: '0_1_1')
            Level_4: "topics" - represented by up to four integers separated by _ (cast as string) (ex: '0_1_1_1')
            Level_5: "subtopics" - represented by up to five integers separated by _ (cast as string) (ex: '0_1_1_1_1')
            Entity: the Wikipedia entity being categorised
    """
    assert alg in ["cooccurrence", "centroids",
                   "imbalanced"], f"Invalid alg argument: {alg}. Expected one of 'cooccurrence', 'centroids', or 'imbalanced'."
    if alg == "cooccurrence":
        return pl.read_parquet("data/taxonomies/community_detection.parquet")
    elif alg == "centroids":
        return pl.read_parquet("data/taxonomies/semantic_centroids.parquet")
    elif alg == "imbalanced":
        return pl.read_parquet("data/taxonomies/semantic_imbalanced.parquet")


def get_group_metadata(level: int = 1, name_type: str = "chatgpt") -> Union[Dict[str, Dict[str, str]], Dict[str, str]]:
    """Gets the names of a taxonomy at a given level using either the top 5 entities in documents in our training corpus or chatgpt (as described in the article.)
        Names are only provided for the co-occurrence taxonomy at the top 3 levels (disciplines, areas, domains).

    Args:
        level (int, optional): Level of the taxonomy to use (1-3). Defaults to 1.
        name_type (str, optional): Naming method to use - chatgpt or entities. Defaults to "chatgpt".

    Returns:
        Union[Dict[str, Dict[str, str]], Dict[str, str]]: 
            if name_type is chatgpt:
                key: taxonomy group label at the specified level (ex: '0' for level 1, '0_1' for level 2, etc.)
                value: Dictionary with name processed chatgpt names:
                    "name": name of group (ex: 'Analytical chemistry')
                    "confidence": confidence score for name provided by chatgpt (out of 100)
                    "discard": any entities that made the naming ambiguous for chatgpt and were discarded (ex: ['John Wiley & Sons'])
            if name_type is "entities":
                key: taxonomy group label at the specified level (ex: '0' for level 1, '0_1' for level 2, etc.)
                value: top 5 most frequent entities in the group (where counts come from count of documents containing that entity in our training corpus) 
    """
    assert level in [
        1, 2, 3], f"Invalid level argument {level}, Expected 1, 2, or 3."
    assert name_type in [
        "chatgpt", "entities"], f"Invalid name_type argument: {name_type}. Expected one of 'chatgpt', 'entities'."
    with open(f"data/group_names/{name_type}/level_{level}.json", "r") as f:
        return json.load(f)
