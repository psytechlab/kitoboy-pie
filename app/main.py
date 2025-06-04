import os
from fastapi import FastAPI
from fastapi.responses import Response
from app.src import NavecIE, RegexIE
from app.utils import format_combined
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
    
    Returns:
        dict: Dictionary containing API name, version and extensions
    """
    return {"name": "triton-like", "version": "1.0.0", "extensions": []}


@app.get("/v2/health/ready")
def ready():
    """
    Health check endpoint.
    
    Returns:
        Response: 200 OK response indicating service is ready
    """
    return Response(status_code=200)


@app.post("/v2/models/pie/infer")
def infer(inputs: TritonRequest):
    """
    Perform inference on input data using multiple information extraction models.
    
    Args:
        inputs (TritonRequest): Request object containing batch of input texts
        
    Returns:
        TritonResponse: Response object containing combined predictions for each input
    """
    request_batched = [x.data for x in inputs.inputs]
    margin_predicts = []
    for ie in app.state.ie_list:
        margin_predicts.append([ie.predict(x) for x in request_batched])
    combined = []
    for one_text_preds in zip(*margin_predicts):
        combined.append([format_combined(preds) for preds in zip(*one_text_preds)])
    output_objs = [OutputObject(shape=[len(x)], data=x) for x in combined]
    return TritonResponse(outputs=output_objs)


@app.get("/v2/models/pie/config")
def config():
    """
    Get model configuration.
    
    Returns:
        dict: Dictionary containing model configuration parameters including:
            - name
            - platform 
            - backend
            - version policy
            - max batch size
    """
    return {
        "name": "pie",
        "platform": "custom",
        "backend": "",
        "version_policy": "",
        "max_batch_size": int(os.environ.get("MAX_BATCH_SIZE", 1)),
    }
