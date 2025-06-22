from transformers import AutoTokenizer, AutoModelForTokenClassification, TokenClassificationPipeline
from transformers import pipeline
from transformers.pipelines import AggregationStrategy

from .base_nlpner import BaseNlpNer

class Transformers(BaseNlpNer):
    def __init__(self, model):
        super().__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForTokenClassification.from_pretrained(model)

        # Create a pipeline for NER
        self.pipeline = pipeline('token-classification',
                                model=self.model,
                                tokenizer=self.tokenizer,
                                aggregation_strategy=AggregationStrategy.SIMPLE
                                )

    def get_entities(self, text):
        entities = self.pipeline(text)

        tags = {}
        tags_insensitive = {}

        for entity in entities:
            label = entity['entity_group']
            text = entity['word']
            if label in self.tags_labels_mapping:
                if self.tags_labels_mapping[label] not in tags:
                    tags[self.tags_labels_mapping[label]] = []
                    tags_insensitive[self.tags_labels_mapping[label]] = []

                if text.lower() not in tags_insensitive[self.tags_labels_mapping[label]]:
                    tags[self.tags_labels_mapping[label]].append(text)
                    tags_insensitive[self.tags_labels_mapping[label]].append(text.lower())

        return tags
