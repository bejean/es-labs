#!python
import argparse
import json
import os
import re
from datetime import datetime
#from readability import Document
#from bs4 import BeautifulSoup

# --- Functions
def parse_date(date_string, default_date):
    """
    Attempts to parse a date string using multiple predefined formats.
    Args:
        date_string (str): The date string to parse.
    Returns:
        datetime.datetime or None: A datetime object if parsing is successful,
                                   otherwise None.
    """
    if date_string == '':
        return default_date

    # Step 1 : date may be inside a complex string
    # Define a list of date patterns in the order of preference
    date_patterns = [
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        r'\d{4}-\d{2}-\d{2}'  # YYYY-MM-DD
    ]
    for pattern in date_patterns:
        match = re.search(pattern, date_string)
        if match:
            date_string = match.group(0)
            break  # Exit the loop once a match is found

    # Step 2 : reformat date
    formats = [
        "%Y-%m-%d",  # e.g., "2023-02-01" (YYYY-MM-DD)
        "%d/%m/%Y",  # e.g., "01/02/2023" (DD/MM/YYYY)
        "%m/%d/%Y",  # e.g., "01/02/2023" (MM/DD/YYYY)
        "%Y/%m/%d",  # e.g., "2023/01/02" (YYY/MM/DD)
        "%d %B %Y",  # e.g., "06 August 2024"
        "%B %d, %Y"  # e.g., "October 31, 2023"
    ]

    for fmt in formats:
        try:
            date_object = datetime.strptime(date_string, fmt)
            date_formatted = date_object.strftime("%Y-%m-%d")
            if date_formatted == '':
                date_formatted = default_date
            return date_formatted
        except ValueError:
            # If parsing fails with the current format, try the next one
            continue

    # If no format matched, return None or raise an error
    return None

def write_output_files(output_list, output_directory, output_count):
    """Writes data to a JSON file."""
    if len(output_list) > 0:
        output_filename = f"{output_count}.json"
        filepath = os.path.join(output_directory, output_filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_list, f, ensure_ascii=False, indent=4)


# --- Main Processing
def main(directory_input, items_by_output_file):
    """Main function"""

    print(f"Starting Crawl post processing {directory_input}")

    directory_output = directory_input + '/clean'

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

    output_count = 0
    output_list = []
    for filename in os.listdir(directory_input):
        if filename.endswith(".json"):
            processed_count +=1
            filepath = os.path.join(directory_input, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    if "article" in data:
                        data["body"] = data.pop("article")

                    if not "body" in data or not data["body"]:
                        processed_skipped += 1
                        continue

                    publication_date = None
                    if "publication_date" in data and data["publication_date"]:
                        publication_date = data["publication_date"]
                    else:
                        if "last_crawled_at" in data and data["last_crawled_at"]:
                            publication_date = data["last_crawled_at"]

                    if publication_date:
                        date_formatted = parse_date(publication_date, "2000-01-01")
                        data["publication_date"] = date_formatted

                    if "full_html" in data and data["full_html"]:
                        #full_html = data.pop("full_html")
                        # https://github.com/buriy/python-readability
                        #doc = Document(full_html)
                        #t = doc.title()
                        #soup = BeautifulSoup(doc.content(), 'html.parser')
                        #text = soup.get_text()
                        data.pop("full_html")

                    output_list.append(data)
                    processed_output +=1

                    if len(output_list) >= items_by_output_file:
                        output_count += 1
                        write_output_files(output_list, directory_output, output_count)
                        output_list = []

                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")
                except Exception as e:
                    print(f"Error indexing {filename}: {e}")

    if len(output_list) > 0:
        write_output_files(output_list, directory_output, output_count)

    print(f"Terminating Crawl post processing (Processed : {processed_count} - Accepted : {processed_output} - Skipped : {processed_skipped})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawler post process script.")
    parser.add_argument("-i", "--input", required=True, type=str, help="Input directory")
    args = parser.parse_args()
    directory_input = args.input

    ITEMS_BY_OUTPUT_FILE = 10
    main(directory_input, ITEMS_BY_OUTPUT_FILE)
