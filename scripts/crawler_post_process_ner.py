#!python
import argparse
import json
import os
from spacy_llm.util import assemble


# --- Functions
def write_output_files(output_list, output_directory, output_count):
    """Writes data to a JSON file."""
    if len(output_list) > 0:
        output_filename = f"{output_count}.json"
        filepath = os.path.join(output_directory, output_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_list, f, ensure_ascii=False, indent=4)


# --- Main Processing
def main(directory_input, api_key_file, ner_config_file, items_by_output_file):
    """Main function"""

    if not os.path.exists(ner_config_file):
        print(f"Error: The file {ner_config_file} was not found.")
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

    tags_labels_mapping = {'ORGANISATION': 'ORG', 'PERSON': 'PER', 'LOCATION': 'LOC'}

    print(f"Starting Crawl post processing {directory_input}")

    directory_output = directory_input + '/ner'

    # Create output directory if it doesn't exist
    if not os.path.exists(directory_output):
        try:
            os.makedirs(directory_output)
        except OSError as e:
            print(f"Failed to create output directory {directory_output}: {e}")
            return

    # === Process files
    processed_count = 0
    processed_skipped = 0
    processed_output = 0

    nlp = assemble(ner_config_file)

    output_count = 0
    output_list = []
    for filename in sorted(os.listdir(directory_input)):
        if filename.endswith(".json"):
            processed_count +=1
            filepath = os.path.join(directory_input, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    print(f"Processing {filepath}")
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = [data]
                    arr = data

                    for doc in arr:
                        text = doc["title"] + doc ["meta_description"]
                        doc_ner = nlp(text)
                        tags = {}
                        tags_insensitive = {}

                        for ent in doc_ner.ents:
                            if ent.label_ in tags_labels_mapping:
                                if tags_labels_mapping[ent.label_] not in tags:
                                    tags[tags_labels_mapping[ent.label_]] = []
                                    tags_insensitive[tags_labels_mapping[ent.label_]] = []

                                if ent.text.lower() not in tags_insensitive[tags_labels_mapping[ent.label_]]:
                                    tags[tags_labels_mapping[ent.label_]].append(ent.text)
                                    tags_insensitive[tags_labels_mapping[ent.label_]].append(ent.text.lower())

                        doc["tags"] = tags

                        output_list.append(doc)
                        processed_output += 1
                        if len(output_list) >= items_by_output_file:
                            output_count += 1
                            write_output_files(output_list, directory_output, output_count)
                            output_list = []

                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    if len(output_list) > 0:
        write_output_files(output_list, directory_output, output_count)

    print(f"Terminating Crawl post processing (Processed : {processed_count} - Accepted : {processed_output} - Skipped : {processed_skipped})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawler post process script.")
    parser.add_argument("-i", "--input", required=True, type=str, help="Input directory")
    parser.add_argument("-k", "--api_key_file", required=False, type=str, help="API Key")
    parser.add_argument("-n", "--ner_config_file", required=False, type=str, help="API Key")
    args = parser.parse_args()
    directory_input = args.input
    api_key_file = args.api_key_file
    ner_config_file = args.ner_config_file

    ITEMS_BY_OUTPUT_FILE = 10
    main(directory_input, api_key_file, ner_config_file, ITEMS_BY_OUTPUT_FILE)
