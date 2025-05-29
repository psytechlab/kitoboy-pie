import re
import yaml
from navec import Navec
from slovnet import NER
from pathlib import Path


class InterfaceInformationExtractor:
    def __init__(self):
        pass

    def predict(self, texts: list[str]):
        pass

    def preprocess_text(self, texts: list[str]):
        pass


class AbstractIE(InterfaceInformationExtractor):
    def predict(self, texts: str | list[str]):
        if isinstance(texts, str):
            texts = [texts]
        preds = []
        for t in texts:
            entites = self.make_prediction(t)
            entites.sort()
            preds.append(";".join(entites))
        return preds

    def make_prediction(self, text: str) -> list[str]:
        pass


class NavecIE(AbstractIE):
    def __init__(self, navec_path, slovnet_path):
        navec = Navec.load(navec_path)
        self.ner = NER.load(slovnet_path)
        self.ner.navec(navec)

    def make_prediction(self, text):
        return list(set([span.type for span in self.ner(text).spans]))


class RegexIE(AbstractIE):
    def __init__(self, dictionary: dict[str:str] | str | Path):
        if isinstance(dictionary, str) or isinstance(dictionary, Path):
            with open(dictionary, "r") as file:
                dictionary = yaml.safe_load(file)
        self.regex2label = self._init_regexes(dictionary)

    def _init_regexes(self, regex2label: dict[str, str]):
        return {re.compile(k): v for k, v in regex2label.items()}

    def make_prediction(self, text: str | list[str]):
        found_entites = []
        for regex, label in self.regex2label.items():
            if regex.search(text) is not None:
                found_entites.append(label)
        return found_entites
