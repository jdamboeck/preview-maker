import pytest
from src.components.template_test import TemplateTestComponent

def test_component_initialization():
    """Test component initialization."""
    component = TemplateTestComponent()
    assert component.name == "Template Test Component"
    assert component.version == "1.0.0"

def test_get_info():
    """Test get_info method."""
    component = TemplateTestComponent()
    info = component.get_info()
    assert "name" in info
    assert "version" in info
    assert "description" in info

def test_test_method():
    """Test the test_method."""
    component = TemplateTestComponent()
    assert component.test_method() == "Template test successful"
