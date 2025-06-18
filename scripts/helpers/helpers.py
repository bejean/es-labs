import os
import numpy as np

def json_convert_to_float64(obj, key):
    if key in obj:
        removed_value = obj.pop(key)
        obj[key] = np.float64(removed_value)
    return obj

def stop_words_load(directory, filename):
    file_path = os.path.join(directory, filename)
    stopwords = []
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as file:
            for line in file:
                stopwords.append(line.strip())  # Remove newline characters
            stopwords = list(set(stopwords))
            stopwords = sorted(stopwords)
    if not stopwords:
        stopwords = None
    return stopwords

def clean_keywords(keywords, stopwords):
    cleaned = []
    for phrase, score in keywords:
        tokens = phrase.strip().split()
        if tokens[-1].lower() in stopwords:
            continue
        cleaned.append((phrase, score))
    return cleaned