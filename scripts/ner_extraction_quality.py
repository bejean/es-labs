#!python

import os
import csv
from collections import defaultdict
import argparse

def concat_in_multiple_files(input_dir, output_file, min_files):
    # Dictionnaire : (col1, col2) => set des fichiers où ils apparaissent
    pair_to_files = defaultdict(set)

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(input_dir, filename)
            try:
                with open(filepath, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    seen_in_file = set()
                    for row in reader:
                        if len(row) >= 2:
                            col1 = row[0].strip()
                            col2 = row[1].strip()
                            seen_in_file.add((col1, col2))
                    for pair in seen_in_file:
                        pair_to_files[pair].add(filename)
            except Exception as e:
                print(f"Erreur dans le fichier {filename} : {e}")

    # Écriture des résultats
    with open(output_file, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(['label', 'text', 'count'])  # en-têtes
        for (col1, col2), files in pair_to_files.items():
            if len(files) >= min_files:
                writer.writerow([col1, col2, len(files)])

def compute_precision_recall(input_dir, result_file):
    # Chargement du résultat global
    retained_pairs = set()
    categories = defaultdict(set)
    with open(result_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            col1 = row["label"].strip()
            col2 = row["text"].strip()
            pair = (col1, col2)
            retained_pairs.add(pair)
            categories[col1].add(col2)

    # Résultat final : fichier => {cat => (precision, recall)}
    metrics = defaultdict(dict)

    for filename in os.listdir(input_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                file_pairs = set()
                file_categories = defaultdict(set)
                for row in reader:
                    if len(row) >= 2:
                        col1 = row[0].strip()
                        col2 = row[1].strip()
                        file_pairs.add((col1, col2))
                        file_categories[col1].add(col2)

                for cat in categories:
                    predicted = {(cat, v) for v in file_categories.get(cat, set())}
                    relevant = {(cat, v) for v in categories[cat]}
                    tp = len(predicted & relevant)
                    fp = len(predicted - relevant)
                    fn = len(relevant - predicted)

                    # Precision = True Positives / (True Positives + False Positives)
                    # Recall = True Positives / (True Positives + False Negatives)

                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                    metrics[filename][cat] = {
                        "precision": round(precision, 3),
                        "recall": round(recall, 3),
                        "tp": tp,
                        "fp": fp,
                        "fn": fn
                    }

        except Exception as e:
            print(f"Erreur lecture {filename} : {e}")

    return metrics


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluate NER extraction quality")
    parser.add_argument("--input", required=True, type=str, help="Input directory")
    parser.add_argument("--output_csv_file", required=False, type=str, help="Output CSV file")
    parser.add_argument("--min_files", required=False, type=int, help="Minimum number of files")
    args = parser.parse_args()
    directory_input = args.input
    output_csv_file = args.output_csv_file
    min_files = args.min_files

    concat_in_multiple_files(directory_input, output_csv_file, min_files)

    results = compute_precision_recall(directory_input, output_csv_file)
    for file, cats in results.items():
        print(f"\n{file}")
        for cat, vals in cats.items():
            print(f"  {cat}: precision={vals['precision']}, recall={vals['recall']}")
