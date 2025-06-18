#!/bin/bash

# --- Default Values ---
JSON_DIR="." # Default to current directory if no parameter is provided
JSON_EXT="json"

# --- Process Command-line Arguments ---
if [[ -n "$1" ]]; then # Check if the first parameter is provided and not empty
  JSON_DIR="$1"
fi

# --- Main Script ---

echo "Prettifying JSON files in directory: $JSON_DIR"

# Check if the directory exists
if [[ ! -d "$JSON_DIR" ]]; then
  echo "Error: Directory '$JSON_DIR' not found."
  exit 1
fi

# Iterate over all files with the specified extension in the directory
for file in "$JSON_DIR"/*."$JSON_EXT"; do
  # Check if the file actually exists (handles cases where no files match the pattern)
  if [[ -f "$file" ]]; then
    echo "Processing: $file"
    
    # Use jq to pretty-print the JSON and overwrite the original file
    if jq '.' "$file" > "${file}.tmp"; then
      mv "${file}.tmp" "$file"
      echo "  Prettified successfully."
    else
      echo "  Error prettifying $file. Skipping."
      rm -f "${file}.tmp" # Clean up temporary file if jq failed
    fi
  fi
done

echo "Done."