from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from transformers.pipelines import AggregationStrategy

from .base_nlpner import BaseNlpNer

class Transformers(BaseNlpNer):
    def __init__(self, model, score_threshold):
        super().__init__()
        if score_threshold is None:
            self.score_threshold = 0.0
        else:
            self.score_threshold = float(score_threshold)
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
            entity_score = entity['score']
            if entity_score >= self.score_threshold:
                entity_label = entity['entity_group']
                entity_text = entity['word']
                super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
