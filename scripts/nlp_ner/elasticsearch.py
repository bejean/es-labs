import requests
from requests.auth import HTTPBasicAuth

from .base_nlpner import BaseNlpNer

class Elasticsearch(BaseNlpNer):
    def __init__(self, es_url, login, ca_cert, model, score_threshold):
        super().__init__()
        self.es_url = es_url
        self.login = login
        self.ca_cert = ca_cert
        self.model=model
        if score_threshold is None:
            self.score_threshold = 0.0
        else:
            self.score_threshold = float(score_threshold)

    def build_infer_url(self) -> str:
        return f"{self.es_url.rstrip('/')}/_ml/trained_models/{self.model}/_infer"

    def build_payload(self, text_field: str) -> dict:
        return {
            "docs": [
                {
                    "text_field": text_field
                }
            ]
        }

    def get_entities(self, text):
        url = self.build_infer_url()
        payload = self.build_payload(text)

        headers = {
            "Content-Type": "application/json"
        }
        request_args = {
            "url": url,
            "json": payload,
            "headers": headers
        }

        if self.login:
            username, password = self.login.split(":", 1)
            request_args["auth"] = HTTPBasicAuth(username, password)

        if url.startswith("https://") and self.ca_cert:
            request_args["verify"] = self.ca_cert
        elif url.startswith("https://"):
            request_args["verify"] = True

        try:
            response = requests.post(**request_args)
            tags = {}
            tags_insensitive = {}

            if response.status_code == 200:
                data = response.json()
                entities = data["inference_results"][0]["entities"]

                for entity in entities:
                    entity_score = entity['class_probability']
                    if entity_score >= self.score_threshold:
                        entity_label = entity['class_name']
                        entity_text = entity['entity']
                        super().add_entity_to_tags(entity_label, entity_text, tags, tags_insensitive)

            return tags

        except Exception as e:
            print(f"An error occurred: {e}")
            return
