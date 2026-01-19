import sys
from TP3.processing import *
from TP3.scoring import *
from TP3.config import INPUT_PATH


def main(queries: list[str], input_path: str, weights: dict) -> dict:
    """
    Execute the search engine pipeline for a list of queries and display results.

    :param queries: List of query strings to be processed.
    :type queries: list[str]
    :param input_path: Path to the JSONL file containing the product catalog.
    :type input_path: str
    :param weights: Dictionary of scoring weights for fields and boosts.
                    Defaults to predefined values in calculate_linear_scoring.
    :type weights: dict
    :return: Dictionary where keys are queries and values are lists of [url, score] pairs for the top 5 results.
    :rtype: dict
    """
    print("=" * 60)
    print("Starting test...")
    print("=" * 60)

    df = load_json_as_df(input_path, lines=True)
    responses = {}
    for q in queries:
        print(f"\nQuery : '{q}'")
        print(f"-" * 40 + "\n")
        results = calculate_linear_scoring(query=q, weights=weights, df=df)
        top5 = list(results.items())[:5]

        if not top5 or top5[0][1] == 0:
            print("No result.")
            continue

        list_urls = []
        for i, (url, score) in enumerate(top5):
            list_urls.append([url, score])
            product = df[df["url"] == url].iloc[0]
            title = product["title"]
            mean_mark = get_reviews(url)["mean_mark"]
            brand = product.get("product_features", "No result.").get(
                "brand", "No result."
            )
            origin = product.get("product_features", "No result.").get(
                "made in", "No result."
            )

            print(f"{i+1}. [ {title} ]")
            print(f"   Score: {score:.4f}")
            print(f"   Mean mark: {mean_mark:.2f}/5")
            print(f"   Brand: {brand}")
            print(f"   Origin: {origin}")
            print(f"   Link: {url}")
            print()

        responses[q] = list_urls

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
