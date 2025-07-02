import unittest
from PIL import Image
import os

from app.services.image_to_text_service import describe_image

class TestImageDescription(unittest.TestCase):
    
    def setUp(self):
        # Caminho para uma imagem de teste
        self.valid_image_path = "./images_examples/macaco-banana.jpg"
        self.invalid_image_path = "./images_examples/nao-existe.jpg"

    def test_description_returns_string(self):
        """Verifica se a descrição gerada é uma string não vazia."""
        result = describe_image(self.valid_image_path)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result.strip()) > 0)

    def test_file_not_found(self):
        """Verifica se a função lida com imagem inexistente."""
        with self.assertRaises(FileNotFoundError):
            describe_image(self.invalid_image_path)

    def test_output_is_meaningful(self):
        """Verifica se a descrição contém palavras-chave esperadas."""
        result = describe_image(self.valid_image_path)
        expected_keywords = ["monkey", "chimp", "banana"]
        self.assertTrue(any(word in result.lower() for word in expected_keywords))

if __name__ == "__main__":
    unittest.main()