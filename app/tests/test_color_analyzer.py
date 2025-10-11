import pytest
from app.services.color_analyzer import hex_to_rgb, suggest_filter

def test_hex_to_rgb_valid_colors():
    """Testa a conversão de cores hex válidas para RGB."""
    assert hex_to_rgb("#FF0000") == (255, 0, 0)
    assert hex_to_rgb("#00FF00") == (0, 255, 0)
    assert hex_to_rgb("#0000FF") == (0, 0, 255)
    assert hex_to_rgb("FFFFFF") == (255, 255, 255)

def test_hex_to_rgb_invalid_format():
    """Testa se a função retorna preto para formatos inválidos."""
    assert hex_to_rgb("#123") == (0, 0, 0)
    assert hex_to_rgb("invalid") == (0, 0, 0)


test_scenarios = [
    ({"accent_color": "#D92E2E", "dominant_colors": ["White"]}, "protanopia", "protanopia-assist"),
    
    ({"accent_color": "#2ED952", "dominant_colors": ["Black"]}, "deuteranopia", "protanopia-assist"),
    
    ({"accent_color": "#D98E2E", "dominant_colors": ["White"]}, "protanopia", "protanopia-assist"),
    
    ({"accent_color": "#FFFFFF", "dominant_colors": ["Red", "Green", "Blue"]}, "protanopia", "protanopia-assist"),
    
    ({"accent_color": "#FF0000", "dominant_colors": ["Red", "White"]}, "protanopia", "protanopia-assist"),
    
    ({"accent_color": "#888888", "dominant_colors": ["Grey", "White"]}, "protanopia", "no-filter"),
    
    ({"accent_color": "#D92E2E", "dominant_colors": ["Red"]}, "tritanopia", "no-filter"),
]

@pytest.mark.parametrize("color_info, blindness_type, expected", test_scenarios)
def test_suggest_filter_scenarios(color_info, blindness_type, expected):
    """Testa vários cenários para a função suggest_filter."""
    suggestion = suggest_filter(color_info, blindness_type)
    assert suggestion == expected