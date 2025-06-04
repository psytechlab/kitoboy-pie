import re
import yaml
from navec import Navec
from slovnet import NER
from pathlib import Path


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
        
        Args:
            texts (list[str]): List of input texts to process
            
        Returns:
            Predictions for the input texts
        """
        pass

    def preprocess_text(self, texts: list[str]):
        """
        Abstract method to preprocess input texts before prediction.
        
        Args:
            texts (list[str]): List of input texts to preprocess
            
        Returns:
            Preprocessed texts
        """
        pass


class AbstractIE(InterfaceInformationExtractor):
    """
    Abstract class for information extraction that implements basic functionality.
    Inherits from InterfaceInformationExtractor.
    """
    
    def predict(self, texts: str | list[str]):
        """
        Predicts entities from input text(s) and formats the output.
        
        Args:
            texts (str | list[str]): Input text or list of texts to process
            
        Returns:
            list[str]: List of predicted entities joined by semicolons for each input text
        """
        if isinstance(texts, str):
            texts = [texts]
        preds = []
        for t in texts:
            entites = self.make_prediction(t)
            entites.sort()
            preds.append(";".join(entites))
        return preds

    def make_prediction(self, text: str) -> list[str]:
        """
        Abstract method to make predictions on a single text.
        
        Args:
            text (str): Input text to process
            
        Returns:
            list[str]: List of predicted entities
        """
        pass


class NavecIE(AbstractIE):
    """
    Implementation of information extraction using Navec embeddings and Slovnet NER.
    """
    
    def __init__(self, navec_path, slovnet_path):
        """
        Initializes the NavecIE with pre-trained models.
        
        Args:
            navec_path: Path to the Navec embeddings model
            slovnet_path: Path to the SlovNet NER model
        """
        navec = Navec.load(navec_path)
        self.ner = NER.load(slovnet_path)
        self.ner.navec(navec)

    def make_prediction(self, text):
        """
        Makes predictions using Slovnet NER model.
        
        Args:
            text (str): Input text to process
            
        Returns:
            list[str]: List of unique entity types found in the text
        """
        return list(set([span.type for span in self.ner(text).spans]))


class RegexIE(AbstractIE):
    """
    Implementation of information extraction using regular expressions.
    """
    
    def __init__(self, dictionary: dict[str:str] | str | Path):
        """
        Initializes the RegexIE with patterns dictionary.
        
        Args:
            dictionary (dict[str:str] | str | Path): Dictionary of regex patterns and their labels,
                                                    or path to YAML file containing patterns
        """
        if isinstance(dictionary, str) or isinstance(dictionary, Path):
            with open(dictionary, "r") as file:
                dictionary = yaml.safe_load(file)
        self.regex2label = self._init_regexes(dictionary)

    def _init_regexes(self, regex2label: dict[str, str]):
        """
        Compiles regex patterns from the dictionary.
        
        Args:
            regex2label (dict[str, str]): Dictionary mapping regex patterns to their labels
            
        Returns:
            dict: Dictionary mapping compiled regex patterns to their labels
        """
        return {re.compile(k): v for k, v in regex2label.items()}

    def make_prediction(self, text: str | list[str]):
        """
        Makes predictions using regex patterns.
        
        Args:
            text (str | list[str]): Input text to process
            
        Returns:
            list[str]: List of labels for matched patterns in the text
        """
        found_entites = []
        for regex, label in self.regex2label.items():
            if regex.search(text) is not None:
                found_entites.append(label)
        return found_entites
