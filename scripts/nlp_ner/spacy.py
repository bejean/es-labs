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
            entity_label = ent.label_
            entity_text = ent.text
            super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
