from flair.data import Sentence
from flair.models import SequenceTagger
from .base_nlpner import BaseNlpNer

# https://github.com/flairNLP/flair
# https://github.com/flairNLP/flair/issues/2299
# https://huggingface.co/flair/ner-french
class Flair(BaseNlpNer):
    def __init__(self, model, score_threshold):
        super().__init__()
        self.tagger = SequenceTagger.load(model)
        if score_threshold is None:
            self.score_threshold = 0.0
        else:
            self.score_threshold = float(score_threshold)

    def get_entities(self, text):
        sentence = Sentence(text)
        self.tagger.predict(sentence)

        tags = {}
        tags_insensitive = {}

        for entity in sentence.get_spans('ner'):
            entity_score = entity.score
            if entity_score >= self.score_threshold:
                entity_label = entity.tag
                entity_text = entity.text
                super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
