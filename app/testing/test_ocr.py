import os
import unittest
from services import ocr

class TestOCR(unittest.TestCase):
    def test_read_text(self):
        reader = ocr.initialize_ocr()
        image_path = os.path.join('app', 'images', 'cat.jpg')
        result = ocr.read_text(reader, image_path)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0, f"OCR retornou string vazia. Resultado: '{result}'")
