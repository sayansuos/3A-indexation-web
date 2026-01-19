import json
import pandas as pd
import string
import os
from TP3.config import *


def load_json(path_in: str, lines=False) -> dict:
    """
    Load the 'path_in' JSON(L) file as a dict.

    :param path_in: Path of the JSONL file.
    :type path_in: str
    :param lines: True if it's a JSONL, False otherwise.
    :type lines: bool
    :return: A dataframe corresponding to the JSONL file.
    :rtype: DataFrame
    """
    if lines:
        data = []
        with open(path_in, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
    else:
        with open(path_in, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data


def load_json_as_df(path_in: str, lines=False) -> pd.DataFrame:
    """
    Load the 'path_in' JSON file as a pandas Dataframe.

    :param path_in: Path of the JSONL file.
    :type path_in: str
    :param lines: True if it's a JSONL, False otherwise.
    :type lines: bool
    :return: A dataframe corresponding to the JSONL file.
    :rtype: DataFrame
    """
    return pd.read_json(path_in, lines=lines)


import json


def save_json(data: dict, file_path: str):
    """
    Save a dict in a JSON file keeping the old data.
    """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    existing_data.update(data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)


def tokenize(text: str) -> list[str]:
    """
    Tranforms the text into a list of words, removing any punctuation or special characters.

    :param text: Text to be processed.
    :type text: str
    :return: List of tokens.
    :rtype: list[str]
    """
    table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    text = text.translate(table)
    return text.strip(string.punctuation).split()


def standardize(tokens: list[str]) -> list[str]:
    """
    Standardizes a list of tokens.

    :param tokens: List of tokens to be processed.
    :type tokens: list[str]
    :return: Lowercased list of tokens.
    :rtype: list[str]
    """
    return [x.lower() for x in tokens]


def remove_stopwords(tokens: list[str]) -> list[str]:
    """
    Removes stopwords from a list of tokens.

    :param tokens: List of tokens to be processed.
    :type tokens: list[str]
    :return: List of tokens without stopwords.
    :rtype: list[str]
    """
    return [x for x in tokens if x not in STOPWORDS]


def process_doc(doc: str) -> list[str]:
    """
    Full text processing pipeline for a single document.

    :param doc: Text to be processed.
    :type doc: str
    :return: List of standardized tokens without stopwords or punctuation.
    :rtype: list[str]
    """
    return remove_stopwords(standardize(tokenize(doc)))


def get_synonyms(token: str) -> list[str]:
    """
    Find all related synonyms for a given word.

    :param token: Word to find synonyms.
    :type token: str
    :return: List of synonyms, or None.
    :rtype: list[str]
    """
    origin_synonyms = load_json(PATH + "/" + SYNONYMS_PATH)
    synonyms = None
    for k, v in origin_synonyms.items():
        if k == token:
            synonyms = origin_synonyms[token]
        if token in v:
            synonyms = origin_synonyms[k]
            synonyms.append(k)
            synonyms.remove(token)
    return synonyms


def process_query(query: str) -> list[str]:
    """
    Process the user query and expand it with synonyms.

    :param query: Text corresponding to the query.
    :type query: str
    :return: List of tokens corresponding to the query words and their synonyms.
    :rtype: list[str]
    """
    q = process_doc(query)
    augment = []
    for token in q:
        synonyms = get_synonyms(token)
        if synonyms:
            augment += synonyms
    return q + augment


def get_reviews(doc_url: str, index_name: str = DOC_REVIEWS) -> dict:
    """
    Retrieve review statistics and ratings for a specific document.

    :param doc_url: URL identifying the document.
    :type doc_url: str
    :param index_name: Name of the JSON index file for reviews (default is 'reviews').
    :type index_name: str
    :return: Dictionary containing 'total_reviews', 'mean_mark', and 'last_rating'.
    :rtype: dict
    """
    index = load_json(PATH + "/" + index_name + "_index.json")
    if doc_url in index.keys():
        return index[doc_url]
    else:
        return {"total_reviews": 0, "mean_mark": None, "last_rating": None}


def get_pos_in_doc(token: str, doc_url: str, field: str) -> list[int]:
    """
    Retrieve the occurrence positions of a token within a specific document field.

    :param token: Word to look up in the index.
    :type token: str
    :param doc_url: URL identifying the document.
    :type doc_url: str
    :param field: Index to search in ('title' or 'description).
    :type field: str
    :return: List of integer positions where the token is found, or an empty list.
    :rtype: list[int]
    """
    if field not in ["title", "description"]:
        raise ValueError("'field' should be 'title' or 'description'.")
    index = load_json(PATH + "/" + field + "_index.json")
    if token in index.keys() and doc_url in index[token]:
        return index[token][doc_url]
    else:
        return []


def get_occ_in_doc(token: str, doc_url: str, field: list[str] = DOC_FIELD) -> int:
    """
    Count total occurrences of a token across multiple document fields.

    :param token: Word to count.
    :type token: str
    :param doc_url: URL identifying the document.
    :type doc_url: str
    :param field: List of document indexes to search.
    :type field: list[str]
    :return: Total number of occurences of the token.
    :rtype: int
    """
    occ = 0
    for f in field:
        index = load_json(PATH + "/" + f + "_index.json")
        if token in index.keys() and doc_url in index[token]:
            if isinstance(index[token], dict):
                occ += len(index[token][doc_url])
            else:
                occ += 1
    return occ


def is_in_doc(token: str, doc_url: str) -> bool:
    """
    Check if a token exists in the document.

    :param token: Word to search for.
    :type token: str
    :param doc_url: URL identifying the document.
    :type doc_url: str
    :return: True if the token is found, False otherwise.
    :rtype: bool
    """
    for field in DOC_FIELD:
        index = load_json(PATH + "/" + field + "_index.json")
        if token in index.keys() and doc_url in index[token]:
            return True
    return False


def contain_1_token(query: str, doc_url: str) -> bool:
    """
    Verify if at least one token from the query exists in the document.

    :param query: Text corresponding to the query.
    :type query: str
    :param doc_url: URL identifying the document.
    :type doc_url: str
    :return: True if at least one query term is present in the document, False otherwise.
    :rtype: bool
    """
    query = process_query(query)
    return any([is_in_doc(x, doc_url) for x in query])


def contain_all_tokens(query: str, doc_url: str) -> bool:
    """
    Check if every single token from the query is present in the document.

    :param query: Text corresponding to the query.
    :type query: str
    :param doc_url: URL identifying the document.
    :type doc_url: str
    :return: True if all query terms are present in the document, False otherwise.
    :rtype: bool
    """
    query = process_query(query)
    return all([is_in_doc(x, doc_url) for x in query])


def get_len_content(
    doc_url: str, df: pd.DataFrame, field: list[str] = DOC_FIELD
) -> int:
    """
    Calculate the total token count of a document across specific fields.

    :param doc_url: URL identifying the document.
    :type doc_url: str
    :param df: DataFrame containing the raw product data.
    :type df: pd.DataFrame
    :param field: List of document indexes to search.
    :type field: list[str]
    :return: Total number of tokens in the document.
    :rtype: int
    """
    len_content = 0
    for f in field:
        if f in ["title", "description"]:
            content = df.loc[df["url"] == doc_url][f].to_list()[0]
            len_content += len(process_doc(content))
        else:
            len_content += 1
    return len_content


def are_positions_successive(all_positions: list[list[int]]) -> bool:
    """
    Check if a sequence of tokens appears consecutively in the text.

    :param all_positions: A list of position lists, where each inner list contains the indices of a token in the document.
    :type all_positions: list[list[int]]
    :return: rue if the tokens form a continuous sequence, False otherwise.
    :rtype: bool
    """
    if not all_positions or not all_positions[0]:
        return False

    for pos in all_positions[0]:
        match = True
        for i in range(1, len(all_positions)):
            if (pos + i) not in all_positions[i]:
                match = False
                break
        if match:
            return True

    return False
