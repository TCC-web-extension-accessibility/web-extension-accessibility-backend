from unittest.mock import MagicMock, patch

@patch.dict('os.environ', {
    'AZURE_CV_ENDPOINT': 'https://fake-endpoint.azure.com',
    'AZURE_CV_KEY': 'fake-api-key-for-testing'
})
def test_analyze_image_colors_with_mock(mocker):
    """
    Testa a função que chama a API do Azure, usando um 'mock' para simular a resposta.
    """
    from app.services.color_analyzer import analyze_image_colors
    mock_api_response = MagicMock()
    mock_api_response.color.is_bw_img = False
    mock_api_response.color.accent_color = "1A2B3C"
    mock_api_response.color.dominant_color_background = "White"
    mock_api_response.color.dominant_color_foreground = "Black"
    mock_api_response.color.dominant_colors = ["White", "Black", "Grey"]

    mock_client = mocker.patch(
        'app.services.color_analyzer.computervision_client.analyze_image_in_stream',
        return_value=mock_api_response
    )

    fake_image_stream = b'fake image data'
    result = analyze_image_colors(fake_image_stream)
    
    mock_client.assert_called_once_with(fake_image_stream, visual_features=['Color'])
    
    # Garante que sua função processou a resposta falsa corretamente
    expected_dict = {
        "is_black_and_white": False,
        "accent_color": "#1A2B3C",
        "dominant_background": "White",
        "dominant_foreground": "Black",
        "dominant_colors": ["White", "Black", "Grey"],
    }
    assert result == expected_dict