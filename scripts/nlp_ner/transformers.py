from transformers import AutoTokenizer, AutoModelForTokenClassification
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
            entity_label = entity['entity_group']
            entity_text = entity['word']
            #entity_score = entity.score
            super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
