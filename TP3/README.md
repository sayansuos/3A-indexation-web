# TP3 Product Search Engine Development

## Goal

The objective of this project is to develop a functional search engine that leverages pre-built inverted indices to retrieve and rank relevant products.

## Projet Structure

The project is organized as follows:

``config.py``: Centralizes paths and scoring weights (e.g., Title vs. Description weight).

``processing.py``: Contains text processing tools (tokenization, normalization, stopword removal) and query expansion logic using country synonyms.

``scoring.py``: Core ranking logic including BM25 calculation, exact phrase matching (proximity), and review-based boosting.

``main.py``: The entry point that orchestrates data loading, query execution, and result formatting

## Implementation Choices

**Query expansion:** To improve recall, the engine expands query terms using a synonyms dictionary (specifically for country origins). For example, a search for "usa" will also match documents indexed under "us".

**Multi-Signal Ranking:** The final relevance score for a document is a weighted sum of several signals:

- BM25: Applied separately to title, description, brand, and origin. This way, a keyword found in the title would be consider more important than one found in a long description, thanks to the field weighting.

- Exact Match (Proximity): A binary boost is applied if the query tokens appear in the exact sequence within the title.

- Review Boost: A non-linear multiplier derived from the mean_mark (rating) and total_reviews (popularity), using a logarithmic scale for the count to avoid overwhelming saturation. It acts as a final multiplier: a very pertinent product with a good grade would still be better than a very pertinent product with a bad grade. However, a well graded product would still has a score of 0 if it is not pertinent. 

**Metadata:** For every query, the engine returns the top 5 results. The output includes:

- Global Metadata: total_documents in the database and filtered_documents (those with a score > 0).

- Document Data: Title, URL, Description, and the calculated final ranking score.


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
python -m TP3.main

# Custom execution
python -m TP3.main path/to/input.jsonl path/to/output_folder
```

The results are saved in a JSONL file ``responses.jsonl`` in the ``output/`` folder. If the output file already exists, the engine updates the file with the new queries without deleting previous results.

## Comments on the results

The results show that the search engine performs well: it ranks products whose titles match the query exactly (with high score around 40). Metadata confirms efficient filtering, reducing the initial database of 156 documents to around 20 documents. Finally, incorporating reviews helps to differentiate between similar products, priorizing the best-rated ones.