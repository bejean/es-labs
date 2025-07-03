#!python

import os
import json
import argparse
import urllib3
from elasticsearch import Elasticsearch, helpers


# === FUNCTION TO PREPARE BULK ACTIONS ===
def generate_bulk_actions(docs, index_name):
    for doc in docs:
        yield {
            "_index": index_name,
            "_id": doc.get("id"),  # Optional: use "id" field if present
            "_source": doc
        }

# --- Main Processing
def main(directory, index_name, es_host, es_username, es_password, insecure, es_ca_cert, bulk_size, max_doc):

    # Connect to your cluster
    es = Elasticsearch(
        es_host,
        basic_auth=(es_username, es_password),
        ca_certs=es_ca_cert,
        verify_certs=not insecure
    )

    # === Process each JSON files
    doc_count = 0
    for filename in sorted(os.listdir(directory)):
        if max_doc > 0 and doc_count >= max_doc:
            break

        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    print(f"Processing {filepath}")
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = [data]
                    arr = data

                    bulk_count = 0
                    while True:
                        try:
                            print(f"bulk {bulk_count} ", end=" ")
                            actions = generate_bulk_actions(arr[bulk_count*bulk_size:(bulk_count+1)*bulk_size], index_name)
                            success_count, failed_items = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)

                            if failed_items:
                                print(f"Warning: Error processing bulk {bulk_count}: {failed_items[0]['index']['error']['reason']}")

                            bulk_count+=1
                            doc_count+=bulk_size
                            if (bulk_count*bulk_size>=len(arr)) or (max_doc>0 and doc_count>=max_doc):
                                break

                        except Exception as e:
                            print(f"Error processing bulk {bulk_count}: {e}")

                    print(f"")

                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
                except Exception as e:
                    print(f"Error indexing {filename}: {e}")


if __name__ == "__main__":
    # === CONFIGURATION ===
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser(description="Crawler post process script.")
    parser.add_argument("--input", required=True, type=str,
                        help="Input directory")
    parser.add_argument("--index", required=True, type=str,
                        help="ES index name")
    parser.add_argument("--host", required=True, type=str,
                        help="ES host:port")
    parser.add_argument("--user", required=True, type=str,
                        help="ES username")
    parser.add_argument("--password", required=True, type=str,
                        help="ES password")
    parser.add_argument('--insecure', required=False, action='store_true',
                        help="No check ES SSL certificate")
    parser.add_argument("--ca_cert", required=False, type=str,
                        help="ES SSL CA certificate")
    parser.add_argument("--bulk_size", required=False, default=10, type=int,
                        help="ES bulk size")
    parser.add_argument("--max_doc", required=False, default=0, type=str,
                        help="maximum number of document to be indexed (0 means no limit)")

    args = parser.parse_args()
    DIRECTORY = args.input
    INDEX_NAME = args.index
    ES_HOST = args.host
    ES_USERNAME = args.user
    ES_PASSWORD = args.password
    ES_CA_CERT = args.ca_cert
    BULK_SIZE = args.bulk_size
    MAX_DOC = args.max_doc
    INSECURE = args.insecure

    if not os.path.exists(DIRECTORY):
        print(f"Error: Input directory not found {DIRECTORY}")
        exit()

    if ES_CA_CERT and not os.path.exists(ES_CA_CERT):
        print(f"Error: ES CA certificate not found {ES_CA_CERT}")
        exit()

    main(DIRECTORY, INDEX_NAME, ES_HOST, ES_USERNAME, ES_PASSWORD, INSECURE, ES_CA_CERT, BULK_SIZE, MAX_DOC)
