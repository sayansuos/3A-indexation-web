import sys
from TP3.processing import *
from TP3.scoring import *
from TP3.config import INPUT_PATH


def main(queries: list[str], input_path: str, weights: dict) -> dict:
    """
    Execute the search engine pipeline for a list of queries and save the results in a dict.

    :param queries: List of query strings to be processed.
    :type queries: list[str]
    :param input_path: Path to the JSONL file containing the product catalog.
    :type input_path: str
    :param weights: Dictionary of scoring weights for fields and boosts. Defaults to predefined values in config.py
    :type weights: dict
    :return: Dictionary where keys are queries and values are dict with the url, title, description and score for the top 5 results.
    :rtype: dict
    """

    df = load_json_as_df(input_path, lines=True)
    total_docs = len(df)
    responses = {}
    for q in queries:
        # Calculating the scores
        results = calculate_linear_scoring(query=q, weights=weights, df=df)
        top5 = list(results.items())[:5]  # Only keep the top5

        if not top5 or top5[0][1] == 0:  # If all scores are 0, we return nothing
            continue

        list_urls = []
        responses[q] = {}
        filtered_docs = sum(1 for score in results.values() if score > 0)
        responses[q]["metadata"] = {}
        responses[q]["metadata"]["total_documents"] = total_docs
        responses[q]["metadata"]["filtered_documents"] = filtered_docs

        for i, (url, score) in enumerate(top5):
            list_urls.append([url, score])
            product = df[df["url"] == url].iloc[0]
            title = product["title"]
            description = product["description"]

            # We enumerate each response
            responses[q][str(i + 1)] = {
                "title": title,
                "url": url,
                "description": description,
                "score": score,
            }

    return responses


if __name__ == "__main__":
    queries = [
        "box of chocolate",
        "leather sneakers",
        "italy",
        "MagicSteps",
        "kids shoes",
    ]

    input_path = INPUT_PATH
    output_path = OUTPUT_PATH
    weights = DEFAULT_WEIGHTS

    if len(sys.argv) > 1:
        input_path = sys.argv[1]

    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    results = main(queries=queries, input_path=input_path, weights=weights)
    save_json(data=results, file_path=output_path)
