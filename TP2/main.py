import sys
import os
from TP2.processing import *


def main(path_in: str, path_out: str):
    print("Loading data...")
    df = load_jsonl_as_df(path_in=path_in)

    print("Building title indexes...")
    title_index = build_inverted_index(df, "title", with_position=True)
    description_index = build_inverted_index(df, "description", with_position=True)

    print("Building feature indexes...")
    brand_index = build_feature_index(df, "brand")
    origin_index = build_feature_index(df, "origin")
    flavors_index = build_feature_index(df, "flavors")
    colors_index = build_feature_index(df, "colors")

    print("Building reviews index...")
    reviews_index = build_review_index(df)

    print(f"Saving indexes to {path_out}/...")
    save_index_to_json(title_index, f"{path_out}/title_index.jsonl")
    save_index_to_json(description_index, f"{path_out}/description_index.jsonl")
    save_index_to_json(brand_index, f"{path_out}/brand_index.jsonl")
    save_index_to_json(origin_index, f"{path_out}/origin_index.jsonl")
    save_index_to_json(flavors_index, f"{path_out}/flavors_index.jsonl")
    save_index_to_json(colors_index, f"{path_out}/colors_index.jsonl")
    save_index_to_json(reviews_index, f"{path_out}/reviews_index.jsonl")

    print("Done!")


if __name__ == "__main__":
    input_path = "TP2/input/products.jsonl"
    output_path = "TP2/output"

    if len(sys.argv) > 1:
        input_path = sys.argv[1]

    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created directory: {output_path}")
    main(path_in=input_path, path_out=output_path)
