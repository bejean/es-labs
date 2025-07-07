from abc import ABC, abstractmethod

class BaseNlpNer(ABC):
    def __init__(self):
        self.tags_labels_mapping = {
            'ORG': 'ORG',
            'ORGANISATION': 'ORG',
            'PER': 'PER',
            'PERSON': 'PER',
            'LOC': 'LOC',
            'LOCATION': 'LOC'
        }

    def contains_alpha(self, text: str) -> bool:
        """
        Returns True if the given text contains at least one alphabetic character, False otherwise.
        :param text: The text to check
        :return: True if the text contains an alphabetic character, False otherwise
        """
        return any(c.isalpha() for c in text)

    def add_entity_to_tags(self, label, text, tags, tags_insensitive):
        text = text.strip()
        if not text:
            return

        special_chars = [
            "'",  # apostrophe droite (ASCII)
            "’",  # apostrophe typographique
            "‘",  # apostrophe ouvrante
            "“",  # guillemet double ouvrant
            "”",  # guillemet double fermant
            '"',  # guillemet droit (ASCII)
            "«",  # guillemet français ouvrant
            "»",  # guillemet français fermant
            "`",  # accent grave
            "´",  # accent aigu
            "‹",  # guillemet simple ouvrant
            "›",  # guillemet simple fermant
            "′",  # prime
            "″",  # double prime
            "-",
            ":",
        ]

        for special_char in special_chars:
            if special_char in text:
                return

        if not self.contains_alpha(text):
            return

        tag_key = self.tags_labels_mapping.get(label)
        if not tag_key:
            return

        if tag_key not in tags:
            tags[tag_key] = []
            tags_insensitive[tag_key] = []

        if text.lower() not in tags_insensitive[tag_key]:
            tags[tag_key].append(text)
            tags_insensitive[tag_key].append(text.lower())
