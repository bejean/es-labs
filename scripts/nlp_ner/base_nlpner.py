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
