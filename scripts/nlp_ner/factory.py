from .spacy import Spacy
from .spacy_llm import SpacyLlm
from .transformers import Transformers
from .flair import Flair
from .elasticsearch import Elasticsearch

class NlpNerFactory:
    @staticmethod
    def build(nlp_ner_type, **kwargs):
        if nlp_ner_type == "spacy":
            return Spacy(kwargs["model"])
        if nlp_ner_type == "spacy_llm":
            return SpacyLlm(kwargs["config_file"])
        if nlp_ner_type == "transformers":
            return Transformers(kwargs["model"], kwargs["score_threshold"])
        if nlp_ner_type == "flair":
            return Flair(kwargs["model"], kwargs["score_threshold"])
        if nlp_ner_type == "elasticsearch":
            return Elasticsearch(kwargs["url"], kwargs["login"], kwargs["model"], kwargs["score_threshold"])
        raise ValueError("Unknown nlp ner type: " + nlp_ner_type)
