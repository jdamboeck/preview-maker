# Gemini AI Integration Guide

## Overview
This document provides a comprehensive guide to the Google Gemini AI integration in the Preview Maker application. It covers the API usage, prompt engineering, response handling, and fallback mechanisms to ensure both human developers and AI assistants understand how to effectively work with this critical component.

## Gemini AI Basics

### What is Gemini AI?
Gemini is Google's multimodal AI model capable of understanding and processing text, images, audio, and code. In Preview Maker, we use Gemini's vision capabilities to analyze images and identify interesting areas for highlighting.

### Key capabilities used in Preview Maker:
- **Image Analysis**: Identify interesting or important details in images
- **Contextual Understanding**: Determine what makes an area interesting based on the image context
- **Coordinate Responses**: Generate precise coordinates for the areas of interest
- **Descriptive Text**: Provide explanations of why an area is interesting

## Integration Architecture

### Component Overview
The Gemini AI integration consists of these main components:

1. **AI Service Interface**: Abstract interface for AI services
2. **Gemini AI Provider**: Concrete implementation for Gemini
3. **Prompt Manager**: Handles prompt construction and templating
4. **Response Parser**: Parses and validates AI responses
5. **Fallback Detector**: Provides detection when AI is unavailable

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  AI Service   │───>│  Gemini API   │───>│   Response    │
│   Interface   │    │    Client     │    │    Parser     │
└───────┬───────┘    └───────────────┘    └───────┬───────┘
        │                                         │
┌───────▼───────┐                         ┌───────▼───────┐
│    Prompt     │                         │    Result     │
│    Manager    │                         │  Validation   │
└───────────────┘                         └───────────────┘
        │                                         ^
        │            ┌───────────────┐            │
        └───────────>│   Fallback    │────────────┘
                     │   Detector    │
                     └───────────────┘
```

## API Integration

### Setting Up Gemini API
```python
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def initialize_gemini(api_key):
    """Initialize the Gemini API with the provided key."""
    genai.configure(api_key=api_key)
    return True

def create_gemini_model(model_name="gemini-1.5-pro-vision"):
    """Create and configure a Gemini model instance."""
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": 0.1,  # Low temperature for more deterministic responses
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 256,
        },
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
    return model
```

### Processing Images with Gemini
```python
async def analyze_image(model, image_data, prompt_text):
    """Analyze an image using Gemini AI."""
    try:
        response = await model.generate_content_async([
            prompt_text,
            image_data
        ])
        return response.text
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return None
```

## Prompt Engineering

### Prompt Structure
The Preview Maker uses a two-part prompt structure:
1. **User Prompt**: Describes what to look for (interesting details, product highlights, etc.)
2. **Technical Prompt**: Specifies the required response format (coordinates and description)

### User Prompt Template
```markdown
Bitte analysiere dieses Bild und identifiziere EIN SPEZIFISCHES {target_type}, das hervorsticht.

Ich benötige, dass du EINEN EINZELNEN, DEUTLICHEN Gegenstand oder ein Merkmal in diesem Produktbild findest - keine allgemeine Fläche.

Analyseprozess:
1. Scanne das gesamte Bild nach dem Hauptprodukt
2. Identifiziere das wichtigste Highlight oder Merkmal dieses Produkts, das:
   - Klar definierte Grenzen hat
   - Sich visuell von seiner Umgebung abhebt
   - Klein genug ist, um ein präzises Ziel zu sein (5-15% der Bildfläche)
   - Detailliert genug ist, um von einer Vergrößerung zu profitieren
   - Ein wichtiges Verkaufsargument oder eine Besonderheit des Produkts darstellt

3. Finde den exakten Mittelpunkt dieses spezifischen Elements
4. Erstelle einen engen Begrenzungsrahmen direkt um NUR dieses einzelne Element
```

### Technical Prompt Template
```markdown
Antworte in ZWEI TEILEN:

1. COORDS: Normalisierte Werte zwischen 0 und 1 im Format x1,y1,x2,y2 wobei:
  - (x1,y1) die obere linke Ecke ist
  - (x2,y2) die untere rechte Ecke ist

2. DESCRIPTION: Eine kurze Beschreibung (1-2 Sätze) dessen, was du identifiziert hast und warum es interessant oder visuell bemerkenswert ist.

Formatiere deine Antwort EXAKT wie folgt:
COORDS: x1,y1,x2,y2
DESCRIPTION: Deine Beschreibung hier.
```

### Target Types
The prompt can be customized with different target types:
- `Produkt-Highlight`: Focus on product features
- `interessantes Detail`: General interesting details
- `technisches Element`: Technical components
- `künstlerisches Element`: Artistic elements

### Prompt Manager Implementation
```python
class PromptManager:
    """Manages prompt templates and generation."""

    def __init__(self, prompt_dir="prompts"):
        self.prompt_dir = prompt_dir
        self.user_template = self._load_template("user_prompt.md")
        self.technical_template = self._load_template("technical_prompt.md")

    def _load_template(self, filename):
        """Load a prompt template from a file."""
        path = os.path.join(self.prompt_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading prompt template {filename}: {e}")
            return ""

    def generate_prompt(self, target_type="interessantes Detail"):
        """Generate a complete prompt with the specified target type."""
        user_prompt = self.user_template.replace("{target_type}", target_type)
        return user_prompt + "\n\n" + self.technical_template
```

## Response Parsing

### Expected Response Format
```
COORDS: 0.4,0.3,0.6,0.5
DESCRIPTION: Das Objektiv der Kamera ist besonders interessant, da es eine spezielle Mehrschichtbeschichtung aufweist, die für die Reduzierung von Lichtreflexionen sorgt.
```

### Response Parser Implementation
```python
class ResponseParser:
    """Parses and validates Gemini AI responses."""

    def __init__(self):
        self.coords_pattern = r"COORDS:\s*(\d*\.\d+),(\d*\.\d+),(\d*\.\d+),(\d*\.\d+)"
        self.description_pattern = r"DESCRIPTION:\s*(.*?)(?:\n|$)"

    def parse_response(self, response_text):
        """
        Parse the response text to extract coordinates and description.

        Returns:
            tuple: (coords, description) where coords is (x1, y1, x2, y2)
            or None if parsing fails
        """
        if not response_text:
            return None

        # Extract coordinates
        coords_match = re.search(self.coords_pattern, response_text)
        if not coords_match:
            return None

        # Extract description
        desc_match = re.search(self.description_pattern, response_text)
        if not desc_match:
            description = ""
        else:
            description = desc_match.group(1).strip()

        # Convert coordinates to float
        try:
            coords = tuple(float(coords_match.group(i)) for i in range(1, 5))
            # Validate coordinates are in range [0, 1]
            if all(0 <= c <= 1 for c in coords):
                return (coords, description)
        except (ValueError, IndexError):
            pass

        return None

    def validate_bounding_box(self, coords):
        """
        Validate that the bounding box is reasonable.

        Args:
            coords: Tuple of (x1, y1, x2, y2)

        Returns:
            bool: True if valid, False otherwise
        """
        x1, y1, x2, y2 = coords

        # Check coordinates are in order (x1 < x2, y1 < y2)
        if x1 >= x2 or y1 >= y2:
            return False

        # Check box isn't too small
        if (x2 - x1) < 0.01 or (y2 - y1) < 0.01:
            return False

        # Check box isn't too large (>50% of image)
        if (x2 - x1) * (y2 - y1) > 0.5:
            return False

        return True
```

## Fallback Detection

### When to Use Fallback
Fallback detection is used when:
1. Gemini API is unavailable (API key missing, network issues)
2. Gemini fails to respond properly
3. Response parsing fails or returns invalid coordinates

### Fallback Detection Algorithm
The fallback detection uses a simple rule-based approach:
1. Find the center of the image
2. Calculate a bounding box around the center (20% of image size)
3. Provide a generic description

```python
def fallback_detection(image):
    """
    Fallback detection when Gemini API is not available.
    Returns coordinates for the center 20% of the image.

    Args:
        image: PIL Image object

    Returns:
        tuple: (coords, description)
    """
    width, height = image.size

    # Define center region (20% of image size)
    center_size = min(width, height) * 0.2
    x_center = width / 2
    y_center = height / 2

    # Calculate normalized coordinates
    x1 = max(0, (x_center - center_size/2) / width)
    y1 = max(0, (y_center - center_size/2) / height)
    x2 = min(1, (x_center + center_size/2) / width)
    y2 = min(1, (y_center + center_size/2) / height)

    coords = (x1, y1, x2, y2)
    description = "Automatisch erkannter zentraler Bereich des Bildes."

    return (coords, description)
```

## Error Handling and Retries

### Common API Errors
1. **Rate Limiting**: Too many requests in a short time
2. **Timeout**: API took too long to respond
3. **Model Error**: Model couldn't process the image
4. **Invalid Response**: Response doesn't match expected format

### Retry Strategy
```python
async def analyze_with_retry(model, image_data, prompt, max_retries=3, backoff_factor=2):
    """
    Analyze image with Gemini, with exponential backoff for retries.

    Args:
        model: Gemini model instance
        image_data: Binary image data
        prompt: Prompt text
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff time

    Returns:
        tuple: (coords, description) or None if all retries fail
    """
    parser = ResponseParser()

    for attempt in range(max_retries + 1):
        try:
            response_text = await analyze_image(model, image_data, prompt)
            if response_text:
                result = parser.parse_response(response_text)
                if result and parser.validate_bounding_box(result[0]):
                    return result
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")

        # Don't sleep on the last attempt
        if attempt < max_retries:
            # Exponential backoff
            sleep_time = backoff_factor ** attempt
            await asyncio.sleep(sleep_time)

    # All retries failed, use fallback
    return fallback_detection(Image.open(io.BytesIO(image_data)))
```

## Testing Gemini Integration

### Mock Responses
For testing without using the actual Gemini API:

```python
class MockGeminiModel:
    """Mock Gemini model for testing."""

    def __init__(self, mock_response=None, should_fail=False):
        self.mock_response = mock_response or """
            COORDS: 0.4,0.3,0.6,0.5
            DESCRIPTION: This is a mock description.
        """
        self.should_fail = should_fail

    async def generate_content_async(self, prompt_parts):
        """Mock the generate_content_async method."""
        if self.should_fail:
            raise Exception("Mock API failure")

        # Create a mock response object
        class MockResponse:
            def __init__(self, text):
                self.text = text

        return MockResponse(self.mock_response)
```

### Test Cases
Key test cases for the Gemini integration:

1. **Successful Analysis**: Verify proper parsing of correct responses
2. **Invalid Responses**: Test handling of malformed responses
3. **API Failures**: Verify fallback behavior on API errors
4. **Rate Limiting**: Test retry behavior with rate limits
5. **Large Images**: Test performance with large images

## Performance Optimization

### Image Preprocessing
To improve Gemini API performance:

1. **Resize Large Images**: Scale down images larger than 1024x1024
2. **Optimize Format**: Convert to JPEG with moderate compression
3. **Remove Metadata**: Strip EXIF and other metadata

```python
def preprocess_image_for_gemini(image_path, max_size=1024):
    """
    Preprocess an image for sending to Gemini API.

    Args:
        image_path: Path to the image file
        max_size: Maximum dimension (width/height)

    Returns:
        bytes: Processed image data
    """
    with Image.open(image_path) as img:
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Resize if too large
        width, height = img.size
        if width > max_size or height > max_size:
            # Maintain aspect ratio
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))

            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        img_bytes = buffer.getvalue()

    return img_bytes
```

### Caching Results
To reduce API calls:

```python
class ResultCache:
    """Cache for Gemini API results."""

    def __init__(self, cache_dir=".cache", max_age_days=30):
        self.cache_dir = cache_dir
        self.max_age = max_age_days * 24 * 60 * 60  # Convert to seconds
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, image_data):
        """Generate a cache key from image data."""
        return hashlib.md5(image_data).hexdigest()

    def get(self, image_data):
        """Get cached result for an image if available."""
        key = self._get_cache_key(image_data)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        if not os.path.exists(cache_file):
            return None

        # Check if cache is too old
        mtime = os.path.getmtime(cache_file)
        if time.time() - mtime > self.max_age:
            os.remove(cache_file)
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            return (tuple(data["coords"]), data["description"])
        except Exception:
            return None

    def set(self, image_data, result):
        """Cache result for an image."""
        key = self._get_cache_key(image_data)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        coords, description = result
        data = {
            "coords": coords,
            "description": description,
            "timestamp": time.time()
        }

        with open(cache_file, 'w') as f:
            json.dump(data, f)
```

## Best Practices

### 1. Prompt Engineering
- Keep prompts clear and specific
- Include explicit instructions about the expected output format
- Specify size constraints for the detected area
- Request normalized coordinates (0-1 range)

### 2. Error Handling
- Always implement fallback detection
- Use exponential backoff for retries
- Validate responses thoroughly before using them
- Log API errors for debugging

### 3. Performance
- Preprocess images before sending to API
- Implement caching for repeated analysis of the same image
- Use async patterns for non-blocking API calls
- Handle large images appropriately

### 4. Testing
- Create a comprehensive set of test images
- Test with the full range of target types
- Mock the API for reliable unit testing
- Test fallback mechanisms by deliberately causing API failures

## Conclusion
Integrating Gemini AI into Preview Maker provides powerful image analysis capabilities that form the core of the application's functionality. By following the patterns and practices in this guide, developers and AI assistants can effectively work with this integration, handle errors gracefully, and optimize performance.