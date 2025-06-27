from abc import ABC, abstractmethod

class BaseNlpNer(ABC):
    def __init__(self):
        self.tags_labels_mapping = {
            'ORG': 'ORG',
            'ORGANISATION': 'ORG',
            'PER': 'PER',
            'PERSON': 'PER',
            'LOC': 'LOC',
            'LOCATION': 'LOC'
        }

    def add_entity_to_tags(self, label, text, tags, tags_insensitive):
        tag_key = self.tags_labels_mapping.get(label)
        if not tag_key:
            return

        if tag_key not in tags:
            tags[tag_key] = []
            tags_insensitive[tag_key] = []

        if text.lower() not in tags_insensitive[tag_key]:
            tags[tag_key].append(text)
            tags_insensitive[tag_key].append(text.lower())
