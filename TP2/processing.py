import urllib
import json
import pandas as pd
import spacy
import string
import numpy as np
from tqdm import tqdm

tqdm.pandas()
nlp = spacy.load("en_core_web_md", disable=["parser"])


def load_jsonl_as_df(path_in: str) -> pd.DataFrame:
    """
    Load the 'path_in' JSONL file and turns it into a pandas Dataframe.

    :param path_in: Path of the JSONL file.
    :type path_in: str
    :return: A dataframe corresponding to the JSONL file.
    :rtype: DataFrame
    """
    return pd.read_json(path_in, lines=True)


def extract_product_id(url: str) -> str:
    """
    Extracts the product's ID from a page with the given 'url'.

    :param url: Url of the product.
    :type url: str
    :return: ID of the product.
    :rtype: str
    """
    url_parsed = urllib.parse.urlparse(url)
    path = url_parsed.path.split("/")
    if path[1] == "product":
        id = path[2]
    else:
        id = None
    return id


def extract_product_variant(url: str) -> list[str]:
    """
    Extracts the product's variant (if it exists) from a page with the given 'url'.

    :param url: Url of the product.
    :type url: str
    :return: List of variants of the products, None if it does not have any.
    :rtype: list[str]
    """
    url_parsed = urllib.parse.urlparse(url)
    url_parsed = urllib.parse.urlparse(url)
    query = url_parsed.query
    params = urllib.parse.parse_qs(query)
    if query and "variant" in params.keys():
        variant = params["variant"]
    else:
        variant = None
    return variant


def get_clean_tokens(doc: str) -> list[str]:
    """
    Gives the tokenized version of the given 'doc', without stopwords and punctuation.

    :param doc: Document we want to process.
    :type doc: str
    :return: List of cleant tokens corresponding.
    :rtype: list[str]
    """
    text = doc.lower().translate(
        str.maketrans(string.punctuation, " " * len(string.punctuation))
    )
    text = nlp(text.lower())
    tokens = [
        token.text
        for token in text
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    return tokens


def get_token_position(token: str, doc: list[str]) -> list[int]:
    """
    Gives the list of positions of a token in a document.

    :param token: Token we want to search for positions.
    :type token: str
    :param doc: Processed tokenized document, without stopwords and punctuation.
    :type doc: list[str]
    :return: List of index positions.
    :rtype: list[int]
    """
    pos = []
    for i, t in enumerate(doc):
        if t == token:
            pos.append(i)

    return pos


def build_inverted_index(
    df: pd.DataFrame, column_name: str, with_position: bool = False
) -> dict:
    """
    Creates the inverted index for all tokens of 'column_name', and their positions if 'with_position' = True.

    :param df: Dataframe with urls and their corresponding title and description.
    :type df: pd.DataFrame
    :param column_name: Name of the colum for inverted index, either 'title' or 'description'.
    :type column_name: str
    :param with_position: True if we also want the token position in each document, False otherwise.
    :type column_name: bool
    :return: Dict with all possible tokens of column 'column_name' as keys and the list of urls containing it as values.
    :rtype: dict
    """
    if not isinstance(column_name, str):
        raise TypeError("'column_name' should be a str instance.")
    if column_name not in ["title", "description"]:
        raise ValueError("'column_name' should take value in ['title', 'description'].")

    processed = f"processed_{column_name}"
    df[processed] = df[column_name].progress_apply(get_clean_tokens)

    inverted_index = {}

    for _, row in df.iterrows():
        current_url = row["url"]
        unique_tokens = set(row[processed])

        for token in unique_tokens:
            if token not in inverted_index:
                inverted_index[token] = []
            if with_position:
                positions = get_token_position(token, row[processed])
                inverted_index[token].append({current_url: positions})
            else:
                inverted_index[token].append(current_url)

    return {k: inverted_index[k] for k in sorted(inverted_index.keys())}


def build_feature_index(df: pd.DataFrame, feature_name: str) -> dict:
    """
    Docstring pour build_feature_index

    :param df: Dataframe with urls and their corresponding features.
    :type df: pd.DataFrame
    :param feature_name: Name of the feature we want to extract.
    :type feature_name: str
    :return: Dict with all possible features of 'features_name' as keys and the list of urls containing it as values.
    :rtype: dict
    """

    if not isinstance(feature_name, str):
        raise TypeError("'feature_name' should be a str instance.")
    if feature_name not in ["brand", "origin", "colors", "flavors"]:
        raise ValueError(
            "'feature_name' should take value in ['brand', 'origin', 'colors', 'flavors']."
        )

    if feature_name == "origin":
        column_name = "made in"
    else:
        column_name = feature_name

    df[feature_name] = df["product_features"].progress_apply(
        lambda x: x[column_name] if column_name in x.keys() else None
    )

    inverted_index = {}

    for _, row in df.iterrows():
        current_url = row["url"]
        if column_name in row["product_features"]:
            feature = row["product_features"][column_name].lower()
            if feature not in inverted_index:
                inverted_index[feature] = []
            inverted_index[feature].append(current_url)

    return inverted_index


def build_review_index(df: pd.DataFrame) -> dict:
    """
    Docstring pour build_review_index

    :param df: Dataframe with urls and their corresponding reviews.
    :type df: pd.DataFrame
    :return: Dict with all urls as keys and a doct of their reviews count, mean ratings and last ratings as values.
    :rtype: dict
    """
    index = {}

    for _, row in df.iterrows():
        current_url = row["url"]
        all_reviews = row["product_reviews"]
        all_ratings = [r["rating"] for r in all_reviews]

        index[current_url] = {}
        index[current_url]["total_reviews"] = len(all_reviews)
        if len(all_reviews) > 0:
            index[current_url]["mean_marks"] = np.mean(all_ratings)
            index[current_url]["last_rating"] = all_ratings[-1]
        else:
            index[current_url]["mean_marks"] = None
            index[current_url]["last_rating"] = None

    return index


def save_index_to_json(data: dict, path_out: str):
    with open(path_out, "w", encoding="utf-8") as f:
        for keys in sorted(data.keys()):
            line = json.dumps({str(keys): data[keys]}, ensure_ascii=False)
            f.write(line + "\n")

    print(f"The file has been saved to: {path_out}!")
