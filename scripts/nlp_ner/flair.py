from flair.data import Sentence
from flair.models import SequenceTagger
from .base_nlpner import BaseNlpNer

# https://github.com/flairNLP/flair
# https://github.com/flairNLP/flair/issues/2299
# https://huggingface.co/flair/ner-french
class Flair(BaseNlpNer):
    def __init__(self, model):
        super().__init__()
        self.tagger = SequenceTagger.load(model)

    def get_entities(self, text):
        sentence = Sentence(text)
        self.tagger.predict(sentence)

        tags = {}
        tags_insensitive = {}

        for entity in sentence.get_spans('ner'):
            entity_label = entity.tag
            entity_text = entity.text
            #entity_score = entity.score
            super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

        return tags
