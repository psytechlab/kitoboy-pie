from pydantic import BaseModel


class InputObject(BaseModel):
    """
    Represents an input object for Triton model inference.

    Attributes:
        name (str): Name of the input
        shape (list[int]): Shape of the input tensor
        datatype (str): Data type of the input
        data (list[str]): Input data as list of strings
    """
    name: str
    shape: list[int]
    datatype: str
    data: list[str]


class TritonRequest(BaseModel):
    """
    Represents a request to Triton inference server.

    Attributes:
        inputs (list[InputObject]): List of input objects for model inference
    """
    inputs: list[InputObject]


class EntitySpan(BaseModel):
    """
    Represents a detected entity span in the input text.

    start is inclusive, end is exclusive, so text[start:end] must equal the
    entity text.
    """
    start: int
    end: int
    label: str


class OutputObject(BaseModel):
    """
    Represents an output object from Triton-like model inference.

    data contains one list of EntitySpan objects for each input text.
    """
    name: str = "predicts"
    datatype: str = "BYTES"
    shape: list[int]
    data: list[str]


class TritonResponse(BaseModel):
    """
    Represents a response from Triton inference server.

    Attributes:
        model_name (str): Name of the model, defaults to "pie_model"
        model_version (str): Version of the model, defaults to "1"
        parameters (dict): Dictionary containing sequence parameters
        outputs (list[OutputObject]): List of output objects from model inference
    """
    model_name: str = "pie_model"
    model_version: str = "1"
    parameters: dict = {
        "sequence_id": 0,
        "sequence_start": False,
        "sequence_end": False,
    }
    outputs: list[OutputObject]
