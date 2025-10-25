import pytest
from fastapi.testclient import TestClient
import io

@pytest.fixture
def client(mocker):
    mocker.patch('app.main.create_tables')
    mocker.patch('app.main.seed_initial_data')

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

def test_describe_image_invalid_file_type(client):
    response = client.post("/api/v1/describe-image/",
                           files={"file": ("teste.txt", b"conteudo qualquer", "text/plain")}
                           )
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an image" 

def test_describe_image_success(client, monkeypatch):
    def mock_image_analyze(_):
        return {"caption":"mocked caption"}

    monkeypatch.setattr("app.api.routes.analyze_image", mock_image_analyze)
    
    fake_image = io.BytesIO(b"fake_image_bytes")

    response = client.post("/api/v1/describe-image/",
                           files={"file":("test.png", fake_image, "image/png")}
                           )
    assert response.status_code == 200
    assert response.json() == {"caption":"mocked caption"}

def test_empty_caption(client, monkeypatch):
    def mock_no_caption(_):
        return {"caption": "no caption"}
    
    monkeypatch.setattr("app.api.routes.analyze_image", mock_no_caption)

    fake_image = io.BytesIO(b"fake_image_bytes")

    response = client.post("/api/v1/describe-image/",
                           files={"file":("test.jpg", fake_image, "image/jpeg")}
                           )
    assert response.status_code == 200
    assert response.json() == {"caption": "no caption"}

