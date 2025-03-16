class TemplateTestComponent:
    """Test component to verify GitHub template workflow."""
    
    def __init__(self):
        self.name = "Template Test Component"
        self.version = "1.0.0"
    
    def get_info(self):
        """Return component information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Component for testing GitHub template workflow"
        }
        
    def test_method(self):
        """Test method for the component."""
        return "Template test successful"
