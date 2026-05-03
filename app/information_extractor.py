import re
from pathlib import Path

import yaml
from navec import Navec
from slovnet import NER


NER_LABEL_MAP = {
    "PER": "NAME",
    "LOC": "ADDRESS",
    "ORG": "ORGANIZATION",
}


class InterfaceInformationExtractor:
    """
    An interface class for information extraction implementations.
    Defines the basic structure for information extractors.
    """
    def __init__(self):
        pass

    def predict(self, texts: list[str]):
        """
        Abstract method to predict entities from input texts.
        """
        pass

    def preprocess_text(self, texts: list[str]):
        """
        Abstract method to preprocess input texts before prediction.
        """
        pass


class AbstractIE(InterfaceInformationExtractor):
    """
    Abstract class for information extraction that implements basic functionality.
    """

    def predict(self, texts: str | list[str]) -> list[list[dict]]:
        """
        Predict entity spans from input text(s).

        Returns one list of entities per input text. Every entity has
        start/end offsets, label and text.
        """
        if isinstance(texts, str):
            texts = [texts]

        preds = []
        for text in texts:
            entities = self.make_prediction(text)
            entities = sorted(entities, key=lambda x: (x["start"], x["end"], x["label"], x["text"]))
            preds.append(entities)
        return preds

    def make_prediction(self, text: str) -> list[dict]:
        """
        Abstract method to make predictions on a single text.
        """
        pass


class NavecIE(AbstractIE):
    """
    Implementation of information extraction using Navec embeddings and Slovnet NER.
    """

    def __init__(self, navec_path, slovnet_path):
        navec = Navec.load(navec_path)
        self.ner = NER.load(slovnet_path)
        self.ner.navec(navec)

    def make_prediction(self, text: str) -> list[dict]:
        """
        Makes span predictions using Slovnet NER model.
        """
        entities = []
        markup = self.ner(text)

        for span in markup.spans:
            label = NER_LABEL_MAP.get(span.type, span.type)
            start = span.start
            end = span.stop
            entities.append(
                {
                    "start": start,
                    "end": end,
                    "label": label,
                    "text": text[start:end],
                }
            )

        return entities


class RegexIE(AbstractIE):
    """
    Implementation of information extraction using regular expressions.
    """

    def __init__(self, dictionary: dict[str, str] | str | Path):
        if isinstance(dictionary, str) or isinstance(dictionary, Path):
            with open(dictionary, "r", encoding="utf-8") as file:
                dictionary = yaml.safe_load(file)
        self.regex2label = self._init_regexes(dictionary)

    def _init_regexes(self, regex2label: dict[str, str]):
        """
        Compiles regex patterns from the dictionary.
        """
        return {re.compile(pattern): label for pattern, label in regex2label.items()}

    def make_prediction(self, text: str) -> list[dict]:
        """
        Makes span predictions using regex patterns.
        """
        found_entities = []
        for regex, label in self.regex2label.items():
            for match in regex.finditer(text):
                found_entities.append(
                    {
                        "start": match.start(),
                        "end": match.end(),
                        "label": label,
                        "text": match.group(0),
                    }
                )
        return found_entities
