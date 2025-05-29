from pydantic import BaseModel


class InputObject(BaseModel):
    name: str
    shape: list[int]
    datatype: str
    data: list[str]


class TritonRequest(BaseModel):
    inputs: list[InputObject]


class OutputObject(BaseModel):
    name: str = "predicts"
    datatype: str = "BYTES"
    shape: list[int]
    data: list[str]


class TritonResponse(BaseModel):
    model_name: str = "pie_model"
    model_version: str = "1"
    parameters: dict = {
        "sequence_id": 0,
        "sequence_start": False,
        "sequence_end": False,
    }
    outputs: list[OutputObject]
