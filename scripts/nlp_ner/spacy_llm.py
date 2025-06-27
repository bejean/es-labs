from spacy_llm.util import assemble
from .base_nlpner import BaseNlpNer

class SpacyLlm(BaseNlpNer):
    def __init__(self, config_file):
        super().__init__()
        self.nlp = assemble(config_file)

    def get_entities(self, text):
        doc = self.nlp(text)
        tags = {}
        tags_insensitive = {}

        for ent in doc.ents:
            entity_label = ent.label_
            entity_text = ent.text
            super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
