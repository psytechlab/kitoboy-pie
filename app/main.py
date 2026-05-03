import os
from fastapi import FastAPI
from fastapi.responses import Response
from app.information_extractor import NavecIE, RegexIE
from app.utils import merge_entities
from app.models import TritonRequest, OutputObject, TritonResponse

app = FastAPI()
app.state.ie_list = [
    NavecIE("data/navec_news_v1_1B_250K_300d_100q.tar", "data/slovnet_ner_news_v1.tar"),
    RegexIE("configs/regex_ie.yml"),
]


@app.get("/v2")
def get_version():
    """
    Get API version information.
    """
    return {"name": "triton-like", "version": "1.0.0", "extensions": []}


@app.get("/v2/health/ready")
def ready():
    """
    Health check endpoint.
    """
    return Response(status_code=200)


@app.post("/v2/models/pie/infer")
def infer(inputs: TritonRequest):
    """
    Perform inference on input data using multiple information extraction models.
    """
    output_objs = []

    for input_obj in inputs.inputs:
        texts = input_obj.data
        extractor_predictions = [ie.predict(texts) for ie in app.state.ie_list]

        combined = []
        for per_text_predictions in zip(*extractor_predictions):
            combined.append(merge_entities(list(per_text_predictions)))

        output_objs.append(OutputObject(shape=[len(combined)], data=combined))

    return TritonResponse(outputs=output_objs)


@app.get("/v2/models/pie/config")
def config():
    """
    Get model configuration.
    """
    return {
        "name": "pie",
        "platform": "custom",
        "backend": "",
        "version_policy": "",
        "max_batch_size": int(os.environ.get("MAX_BATCH_SIZE", 1)),
    }
