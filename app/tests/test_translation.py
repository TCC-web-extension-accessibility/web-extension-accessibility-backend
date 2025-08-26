from fastapi.testclient import TestClient
from main import app
import pytest
from schemas.translation_schema import Translation_schema

client = TestClient(app)

def test_translation_success(monkeypatch):
    def mock_translation_success(to_language, text_list, from_language):
        return {"test": "teste", "car": "carro"}
    
    monkeypatch.setattr("api.routes.translate_list", mock_translation_success)

    fake_translation_schema = Translation_schema(from_language = "en",
                                                 text_list = ["test", "car"], 
                                                 to_language = "pt")


    response = client.post("/api/v1/translate/", json=fake_translation_schema.model_dump())

    assert response.status_code == 200
    assert response.json() == {"test":"teste", "car":"carro"} 
    
