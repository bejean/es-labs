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
            label = ent.label_
            text = ent.text
            if label in self.tags_labels_mapping:
                if self.tags_labels_mapping[label] not in tags:
                    tags[self.tags_labels_mapping[label]] = []
                    tags_insensitive[self.tags_labels_mapping[label]] = []

                if text.lower() not in tags_insensitive[self.tags_labels_mapping[label]]:
                    tags[self.tags_labels_mapping[label]].append(text)
                    tags_insensitive[self.tags_labels_mapping[label]].append(text.lower())

        return tags
