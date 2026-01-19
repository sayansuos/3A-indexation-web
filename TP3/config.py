from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))
PATH = "TP3/input"
INPUT_PATH = "TP3/input/rearranged_products.jsonl"
OUTPUT_PATH = "TP3/output/responses.jsonl"
SYNONYMS_PATH = "origin_synonyms.json"
DOC_FIELD = ["title", "description", "origin", "brand"]
DOC_REVIEWS = "reviews"
DEFAULT_WEIGHTS = {
    "title": 3.0,
    "description": 1.5,
    "features": 0.8,
    "proximity": 2.0,
    "avg_mark": 0.4,
    "count_mark": 0.2,
}
