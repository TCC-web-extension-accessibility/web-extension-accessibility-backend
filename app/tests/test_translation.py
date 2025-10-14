import pytest
from fastapi.testclient import TestClient
from app.schemas.translation_schema import Translation_schema

@pytest.fixture
def client(mocker):
    mocker.patch('app.main.create_tables')
    mocker.patch('app.main.seed_initial_data')
    
    from app.main import app
    
    with TestClient(app) as test_client:
        yield test_client

def test_translation_success(client, monkeypatch):
    def mock_translation_success(to_language, text_list, from_language):
        return {"test": "teste", "car": "carro"}
    
    monkeypatch.setattr("app.api.routes.translate_list", mock_translation_success)

    fake_translation_schema = Translation_schema(from_language = "en",
                                                 text_list = ["test", "car"], 
                                                 to_language = "pt")


    response = client.post("/api/v1/translate/", json=fake_translation_schema.model_dump())

    assert response.status_code == 200
    assert response.json() == {"test":"teste", "car":"carro"} 
    
