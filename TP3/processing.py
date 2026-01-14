import urllib
import json
import pandas as pd
import spacy
import string
import nltk
from nltk.corpus import stopwords
import numpy as np
from tqdm import tqdm

nltk.download("stopwords")
STOPWORDS = stopwords.words("english")
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


def load_json(path_in: str, lines=False) -> dict:
    if lines:
        data = []
        with open(path_in, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
    else:
        with open(path_in, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data


def tokenize(text: str):
    return text.split()


def normalize(tokens: list[str]):
    translator = str.maketrans("", "", string.punctuation)
    return [x.lower().translate(translator) for x in tokens]


def remove_stopwords(tokens: list[str]):
    return [x for x in tokens if x not in STOPWORDS]


def process_doc(doc: str) -> list[str]:
    """
    Gives the tokenized version of the given 'doc', without stopwords and punctuation.

    :param doc: Document we want to process.
    :type doc: str
    :return: List of cleant tokens corresponding.
    :rtype: list[str]
    """
    return remove_stopwords(normalize(tokenize(doc)))


def get_synonyms(token: str, synonyms_path: str) -> list[str]:
    origin_synonyms = load_json(synonyms_path)
    synonyms = None
    for k, v in origin_synonyms.items():
        if k == token:
            synonyms = origin_synonyms[token]
        if token in v:
            synonyms = origin_synonyms[k]
            synonyms.append(k)
            synonyms.remove(token)
    return synonyms


def process_queries(query: str, synonyms_path: str) -> list[str]:
    q = process_doc(query)
    augment = []
    for token in q:
        synonyms = get_synonyms(token, synonyms_path)
        if synonyms:
            augment += synonyms
    return q + augment
