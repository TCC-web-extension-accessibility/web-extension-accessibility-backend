from fastapi.testclient import TestClient
from main import app
from services.image_description import analyze_image
import pytest
import io

client = TestClient(app)

def test_describe_image_invalid_file_type():
    response = client.post("/api/v1/describe-image/",
                           files={"file": ("teste.txt", b"conteudo qualquer", "text/plain")}
                           )
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an image" 

def test_describe_image_success(monkeypatch):
    def mock_image_analyze(_):
        return {"caption":"mocked caption"}

    monkeypatch.setattr("api.routes.analyze_image", mock_image_analyze)
    
    fake_image = io.BytesIO(b"fake_image_bytes")

    response = client.post("/api/v1/describe-image/",
                           files={"file":("test.png", fake_image, "image/png")}
                           )
    assert response.status_code == 200
    assert response.json() == {"caption":"mocked caption"}

def test_empty_caption(monkeypatch):
    def mock_no_caption(_):
        return {"caption": "no caption"}
    
    monkeypatch.setattr("api.routes.analyze_image", mock_no_caption)

    fake_image = io.BytesIO(b"fake_image_bytes")

    response = client.post("/api/v1/describe-image/",
                           files={"file":("test.jpg", fake_image, "image/jpeg")}
                           )
    assert response.status_code == 200
    assert response.json() == {"caption": "no caption"}

