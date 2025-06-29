#!python
import argparse
import json
import os
import time
from nlp_ner import NlpNerFactory


# --- Functions
def write_output_files(output_list, output_directory, output_count):
    """Writes data to a JSON file."""
    if len(output_list) > 0:
        output_filename = f"{output_count}.json"
        filepath = os.path.join(output_directory, output_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_list, f, ensure_ascii=False, indent=4)


def build_text(doc):
    title = doc.get("title", "").strip()
    if title and title[-1] not in ".!?":
        title += "."
    meta = doc.get("meta_description", "").strip()
    return f"{title} {meta}".strip()


# --- Main Processing
def main(directory_input, ner_mode, api_key_file, ner_config_file, ner_model, score_threshold, url, login, ca_cert_file, output_csv_file, items_by_output_file):
    #
    """Main function"""

    if ner_config_file and not os.path.exists(ner_config_file):
        print(f"Error: The NER configuration file {ner_config_file} was not found.")
        return

    if api_key_file and not os.path.exists(api_key_file):
        print(f"Error: The API key file {api_key_file} was not found.")
        return

    if ca_cert_file and not os.path.exists(ca_cert_file):
        print(f"Error: The CA CRT file {ca_cert_file} was not found.")
        return

    if output_csv_file:
        output_csv_file_path = os.path.dirname(output_csv_file)
        if not os.path.isdir(output_csv_file_path):
            print(f"Error: The folder for CSV file {output_csv_file_path} was not found.")
            return

    if api_key_file:
        try:
            with open(api_key_file, 'r') as file:
                api_key_file_content = file.read()
                parts = api_key_file_content.split(":")
                os.environ[parts[0]] = parts[1]
        except FileNotFoundError:
            print(f"Error: The file {api_key_file} was not found.")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

    print(f"Starting Crawl post processing {directory_input}")

    if not output_csv_file:
        directory_output = directory_input + '/ner'

        # Create output directory if it doesn't exist
        if not os.path.exists(directory_output):
            try:
                os.makedirs(directory_output)
            except OSError as e:
                print(f"Failed to create output directory {directory_output}: {e}")
                return

    else:
        csv_rows = {}

    # === Process files
    processed_file_count = 0
    processed_item_skipped = 0
    processed_item_output = 0

    match ner_mode:
        case 'spacy':
            nlp = NlpNerFactory.build("spacy", model=ner_model)
        case 'spacy_llm':
            nlp = NlpNerFactory.build("spacy_llm", config_file=ner_config_file)
        case 'transformers':
            nlp = NlpNerFactory.build("transformers", model=ner_model, score_threshold=score_threshold)
        case 'flair':
            nlp = NlpNerFactory.build("flair", model=ner_model, score_threshold=score_threshold)
        case 'elasticsearch':
            nlp = NlpNerFactory.build("elasticsearch", model=ner_model, score_threshold=score_threshold, url=url, login=login, ca_cert=ca_cert_file)
        case _:
            print("Invalid NER mode")
            return

    output_count = 0
    output_list = []
    total_entities_count = 0
    for filename in sorted(os.listdir(directory_input)):
        if filename.endswith(".json"):
            processed_file_count +=1

            filepath = os.path.join(directory_input, filename)
            with (open(filepath, 'r', encoding='utf-8') as file):
                try:
                    print(f"Processing {filepath}")
                    start_time_file = time.time()
                    file_entities_count = 0

                    data = json.load(file)
                    if not isinstance(data, list):
                        data = [data]
                    arr = data

                    for doc in arr:
                        id = doc["id"]
                        try:
                            text = build_text(doc)
                            tags = nlp.get_entities(text)
                            if output_csv_file:
                                for tag in tags:
                                    entities = tags.get(tag)
                                    file_entities_count += len(entities)
                                    for entitie in entities:
                                        k = tag+':'+entitie
                                        if not k in csv_rows:
                                            csv_rows[k]=1
                                        else:
                                            csv_rows[k]=csv_rows[k]+1
                            else:
                                doc["tags"] = tags
                                output_list.append(doc)

                            processed_item_output += 1
                            if not output_csv_file and (len(output_list) >= items_by_output_file):
                                output_count += 1
                                write_output_files(output_list, directory_output, output_count)
                                output_list = []

                        except Exception as e:
                            processed_item_skipped += 1
                            print(f"Error processing document {id}: {e}")

                    end_time_file = time.time()
                    duration = end_time_file - start_time_file
                    file_items_count = len(arr)
                    total_entities_count += file_entities_count

                    print(f"File duration: {duration:.2f} seconds for {file_items_count} documents / {file_entities_count} entities")

                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    if not output_csv_file and (len(output_list) > 0):
        write_output_files(output_list, directory_output, output_count)

    if output_csv_file:
        import csv
        with open(output_csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in csv_rows:
                cols = row.split(":")
                cols.append(csv_rows[row])
                writer.writerow(cols)

    print(f"Terminating Crawl post processing (Processed files : {processed_file_count} - Accepted items : {processed_item_output} - Skipped items : {processed_item_skipped} - Total entities count : {total_entities_count} )")

if __name__ == "__main__":

    start_time = time.time()

    parser = argparse.ArgumentParser(description="Crawler post process script.")
    parser.add_argument("--input", required=True, type=str, help="Input directory")
    parser.add_argument("--mode", required=True, type=str, help="Mode")
    parser.add_argument("--api_key_file", required=False, type=str, help="API Key")
    parser.add_argument("--config_file", required=False, type=str, help="Configuration file")
    parser.add_argument("--model", required=False, type=str, help="Model name")
    parser.add_argument("--score_threshold", required=False, type=str, help="Entity score threshold : 0.00 (default) to 1.00")
    parser.add_argument("--output_csv_file", required=False, type=str, help="Output CSV file")
    parser.add_argument("--url", required=False, type=str, help="API Url")
    parser.add_argument("--login", required=False, type=str, help="API Login")
    parser.add_argument("--ca_cert", required=False, type=str, help="API CA Certificate")
    args = parser.parse_args()
    directory_input = args.input
    ner_mode = args.mode
    api_key_file = args.api_key_file
    ner_config_file = args.config_file
    ner_model = args.model
    score_threshold = args.score_threshold
    output_csv_file = args.output_csv_file
    url = args.url
    login = args.login
    ca_cert = args.ca_cert

    ITEMS_BY_OUTPUT_FILE = 10
    main(directory_input, ner_mode, api_key_file, ner_config_file, ner_model, score_threshold, url, login, ca_cert, output_csv_file, ITEMS_BY_OUTPUT_FILE)

    end_time = time.time()
    duration = end_time - start_time

    print(f"Script duration: {duration:.2f} seconds")

