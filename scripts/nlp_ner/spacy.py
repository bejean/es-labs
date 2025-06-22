import spacy
from .base_nlpner import BaseNlpNer

class Spacy(BaseNlpNer):
    def __init__(self, model):
        super().__init__()
        self.nlp = spacy.load(model)

    def get_entities(self, text):
        doc = self.nlp(text)
        tags = {}
        tags_insensitive = {}

        for ent in doc.ents:
            label = ent.label_
            text = ent.text
            if ent.label_ in self.tags_labels_mapping:
                if self.tags_labels_mapping[ent.label_] not in tags:
                    tags[self.tags_labels_mapping[ent.label_]] = []
                    tags_insensitive[self.tags_labels_mapping[ent.label_]] = []

                if ent.text.lower() not in tags_insensitive[self.tags_labels_mapping[ent.label_]]:
                    tags[self.tags_labels_mapping[ent.label_]].append(ent.text)
                    tags_insensitive[self.tags_labels_mapping[ent.label_]].append(ent.text.lower())

        return tags
