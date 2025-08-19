import unittest
from unittest.mock import MagicMock, patch
from app.services.image_description import ImageDescriptionService

class TestImageDescriptionService(unittest.TestCase):
    @patch("app.services.image_description.ComputerVisionClient")
    def test_describe_image_bytes_success(self, MockClient):
        # Setup
        mock_caption = MagicMock()
        mock_caption.text = "a cat sitting on a couch"

        mock_result = MagicMock()
        mock_result.captions = [mock_caption]

        mock_client_instance = MockClient.return_value
        mock_client_instance.describe_image_in_stream.return_value = mock_result

        service = ImageDescriptionService("fake_endpoint", "fake_key")

        # Mock image bytes
        image_bytes = b"fake_image_data"

        result = service.describe_image_bytes(image_bytes)

        self.assertEqual(result, "a cat sitting on a couch")

    @patch("app.services.image_description.ComputerVisionClient")
    def test_describe_image_bytes_no_caption(self, MockClient):
        # Setup
        mock_result = MagicMock()
        mock_result.captions = []

        mock_client_instance = MockClient.return_value
        mock_client_instance.describe_image_in_stream.return_value = mock_result

        service = ImageDescriptionService("fake_endpoint", "fake_key")

        result = service.describe_image_bytes(b"image_data")

        self.assertEqual(result, "No description found.")

    @patch("app.services.image_description.ComputerVisionClient")
    def test_describe_image_bytes_error(self, MockClient):
        # Simulate exception
        mock_client_instance = MockClient.return_value
        mock_client_instance.describe_image_in_stream.side_effect = Exception("Some error")

        service = ImageDescriptionService("fake_endpoint", "fake_key")

        result = service.describe_image_bytes(b"bad_data")

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
