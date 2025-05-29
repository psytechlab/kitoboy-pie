from __future__ import annotations
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/v2")
    assert response.status_code == 200
    assert response.json() == {"name":"triton-like",
            "version":"1.0.0",
            "extensions":[]
            }

def test_health():
    response = client.get("/v2/health/ready")
    assert response.status_code == 200

def test_config():
    response = client.get("/v2/models/pie/config")
    assert response.json() == {"name": "pie", 
                               "platform": "custom",
                               "backend": "",
                               "version_policy": "",
                               "max_batch_size": 1}
    
def test_config_with_diff_batchsize():
    import os
    os.environ["MAX_BATCH_SIZE"] = "4"
    response = client.get("/v2/models/pie/config")
    assert response.json() == {"name": "pie", 
                               "platform": "custom",
                               "backend": "",
                               "version_policy": "",
                               "max_batch_size": 4}
    
def test_phone_number_detection(phone_number_collection):
    input_json, output_labels = phone_number_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]

def test_bank_card_number_detection(bank_card_collection):
    input_json, output_labels = bank_card_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]

def test_email_detection(emails_collection):
    input_json, output_labels = emails_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]

def test_telegram_link_detection(telegram_link_collection):
    input_json, output_labels = telegram_link_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]


def test_vk_link_detection(vk_link_collection):
    input_json, output_labels = vk_link_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]

def test_ner_detection(ner_collection):
    input_json, output_labels = ner_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]

def test_multi_entity_detection(multiple_entity_collection):
    input_json, output_labels = multiple_entity_collection
    output = client.post("/v2/models/pie/infer", json=input_json)
    assert output_labels == output.json()["outputs"][0]["data"]