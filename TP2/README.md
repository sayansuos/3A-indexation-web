# TP2 Search Engine Index Development

## Goal

The objective of this project is to build various types of indexes from an e-commerce product dataset. These indexes are the foundation of a search engine.

## Projet Structure

- ``processing.py``: Core logic containing functions for data cleaning, tokenization, and index construction.

- ``main.py``: Main execution script that orchestrates the loading, processing, and saving of indexes.

- ``input/``: Directory containing the source products.jsonl file.

- ``output/``: Directory where the generated JSONL indexes are stored.

## Indexes Structure

We have implemented three types of indexes:

**1/ Inverted Index with Positions**: ``description_index.jsonl`` and ``title_index.jsonl``

- Stored as a dictionary where each key is a unique token (word), and the value is a list of documents with the specific positions of the token in that document.

- Format: ``{"token": [{"url1": [pos1, pos2]}, {"url2": [pos1]}, ...], ...}``

**2/ Simple Inverted Index (Features)**: ``brand_index.jsonl``, ``origin_index.jsonl``, ``colors_index.jsonl`` and ``flavors_index.jsonl``

- Maps a specific product feature (brand, origin, flavors, colors) to the list of URLs sharing that feature.

- Format: ``{"brand_name": ["url1", "url2", ...], ...}``

**3/ Non-Inverted Index**: ``reviews_index.jsonl``

- A direct lookup table used for ranking. It stores metadata for each product URL.

- Format: ``{"url": {"total_reviews": _, "mean_marks": _, "last_rating": _}, ...}``

## Implementation Choices

For text processing, we chose spaCy (en_core_web_md) to have a better handling of English semantics, allowing for accurate stop-word removal and lemmatization.

The Inverted Index with Position was implemented by first cleaning the text (lowercasing and punctuation removal) and then mapping each token to a list of dictionaries. Each dictionary contains the document URL as a key and a list of integers representing the token's precise indices.

For Product Features, we implemented a extraction logic that targets specific keys (brand, origin, colors, flavors) within the nested JSON structure, converting them into a categorical inverted index for fast filtering. The inclusion of colors and flavors as indexed features enhances the search experience by enabling faceted filtering, allowing users to narrow down results based on specific product attributes beyond just keywords.

Finally, the Reviews Index was designed as a direct non-inverted structure, storing pre-calculated aggregates like mean ratings, counts and last rating.

## Executing the code

To execute the code, first set up a virtual environment (optional but recommanded) and install dependencies.

```bash
# Virtual environment
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# Prerequisites
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

To produce the different results, run:

```bash
# Default execution
python -m TP2.main

# Custom execution
python -m TP2.main path/to/input.jsonl path/to/output_folder
```

After running, the ``output/`` folder will contain: ``title_index.jsonl``, ``description_index.jsonl``, ``brand_index.jsonl``, ``origin_index.jsonl``, ``colors_index.jsonl``, ``flavors_index.jsonl`` and ``reviews_index.jsonl``.