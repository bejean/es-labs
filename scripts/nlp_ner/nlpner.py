from abc import ABC, abstractmethod

class NlpNer(ABC):
    @abstractmethod
    def get_entities(self, text):
        pass
