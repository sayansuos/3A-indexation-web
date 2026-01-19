import math
import pandas as pd
import numpy as np
from TP3.config import *
from TP3.processing import *


def calculate_bm25(
    query: str, field: str, df: pd.DataFrame, b: float = 0.75, k: float = 1.2
) -> dict:
    """
    Calculate the BM25 relevance score for each document against a query.

    :param query: Text corresponding to the query.
    :type query: str
    :param field: List of document indexes to search.
    :type field: str
    :param df: DataFrame containing the raw product data.
    :type df: pd.DataFrame
    :param b: Length normalization parameter (default 0.75).
    :type b: float
    :param k: Term frequency saturation parameter (default 1.2).
    :type k: float
    :return: Dictionary mapping document URLs to their calculated BM25 scores.
    :rtype: dict
    """
    query = process_query(query)
    n_docs = len(df)

    all_lengths = df["url"].apply(
        lambda x: get_len_content(doc_url=x, df=df, field=[field])
    )
    avg_len = all_lengths.mean()

    bm25 = {url: 0 for url in df["url"]}

    for token in query:
        doc_freq = sum(df["url"].apply(lambda x: is_in_doc(token, x)))
        if doc_freq != 0:
            idf = np.log(n_docs / doc_freq)
            for i, url in enumerate(df["url"]):
                f = get_occ_in_doc(token, url, [field])
                if f > 0:
                    len_doc = all_lengths.iloc[i]
                    num = f * (k + 1)
                    den = f + k * (1 - b + b * len_doc / avg_len)
                    bm25[url] += idf * (num / den)

    return bm25


def is_exact_match(query: str, field: str, df: pd.DataFrame) -> dict:
    """
    Identify documents containing the query as an exact consecutive phrase.

    :param query: Text corresponding to the query.
    :type query: str
    :param field: List of document indexes to search.
    :type field: str
    :param df: DataFrame containing the raw product data.
    :type df: pd.DataFrame
    :return: Dictionary mapping URLs to 1 (match found) or 0 (no match).
    :rtype: dict
    """
    match = {url: 0 for url in df["url"]}
    query = process_query(query)

    for url in df["url"]:
        all_positions = []
        for token in query:
            positions = get_pos_in_doc(token, url, field)
            all_positions.append(positions)
        if are_positions_successive(all_positions):
            match[url] = 1

    return match


def calculate_reviews_boost(
    df: pd.DataFrame, weights: dict, index_name: str = DOC_REVIEWS
) -> dict:
    """
    Calculate a boost factor for documents based on user ratings and popularity.

    :param df: DataFrame containing the raw product data.
    :type df: pd.DataFrame
    :param weights: Dictionary of importance weights for various scoring factors.
    :type weights: dict
    :param index_name: Name of the JSON index file for reviews (default is 'reviews').
    :type index_name: str
    :return: Dictionary mapping document URLs to their calculated boost multipliers.
    :rtype: dict
    """
    boost = {}

    for _, row in df.iterrows():
        url = row["url"]
        marks = get_reviews(url, index_name)
        mean_mark = marks["mean_mark"]
        count = marks["total_reviews"]

        mark_factor = 1 + (mean_mark / 5) * weights["avg_mark"]
        count_factor = 1 + math.log10(count + 1) * weights["count_mark"]

        boost[url] = mark_factor * count_factor

    return boost


def calculate_linear_scoring(query: str, df: pd.DataFrame, weights: dict) -> dict:
    """
    Calculate a weighted final relevance score and rank all documents.

    :param query: Text corresponding to the query.
    :type query: str
    :param df: DataFrame containing the raw product data.
    :type df: pd.DataFrame
    :param weights: Dictionary of importance weights for various scoring factors.
    :type weights: dict
    :return: Dictionary of URLs and their final scores, sorted from highest to lowest.
    :rtype: dict
    """

    all_score_title = calculate_bm25(query=query, field="title", df=df)
    all_score_desc = calculate_bm25(query=query, field="description", df=df)
    all_score_brand = calculate_bm25(query=query, field="brand", df=df)
    all_score_origin = calculate_bm25(query=query, field="origin", df=df)
    all_score_proximity = is_exact_match(query=query, field="title", df=df)
    all_review_boost = calculate_reviews_boost(weights=weights, df=df)

    scores = {}

    for url in df["url"]:
        score_title = all_score_title.get(url, 0)
        score_desc = all_score_desc.get(url, 0)
        score_brand = all_score_brand.get(url, 0)
        score_origin = all_score_origin.get(url, 0)
        score_proximity = all_score_proximity.get(url, 0)
        review_boost = all_review_boost.get(url, 1)

        score = (
            score_title * weights["title"]
            + score_desc * weights["description"]
            + (score_brand + score_origin) * weights["features"]
            + score_proximity * weights["proximity"]
        ) * review_boost
        scores[url] = score

    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
