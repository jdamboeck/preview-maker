# Performance Testing

This document details the approach to performance testing for the rebuilt Preview Maker application, with a focus on Docker-based testing.

## Performance Testing Approach

Performance tests verify that the application meets performance requirements. They focus on measuring key performance metrics such as response time, throughput, and resource usage.

### Key Performance Metrics

1. **Image Loading Time**: Time to load and process images
2. **UI Responsiveness**: Frame rate during UI operations
3. **Memory Usage**: Peak memory usage during operation
4. **API Response Time**: Time to receive and process API responses

## Docker-Based Performance Testing

Performance tests are run in the Docker test container to ensure a consistent environment:

```bash
# Run all performance tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/performance/

# Run specific performance tests
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/performance/test_image_loading_performance.py
```

## Performance Test Structure

Performance tests should follow this structure:

1. **Setup**: Create and configure the components being tested
2. **Benchmark**: Measure the performance of the operation
3. **Verification**: Verify that the performance meets requirements

Example:

```python
def test_image_loading_performance(benchmark):
    """Test that image loading meets performance requirements."""
    # Setup
    processor = ImageProcessor()
    test_image_path = "test_data/test_image_12mp.jpg"

    # Benchmark
    result = benchmark(processor.process_image, test_image_path)

    # Verification
    assert result is not None
    assert benchmark.stats.stats.mean < 0.2  # Less than 200ms
```

## Memory Usage Testing

For memory usage testing, use the memory_profiler package:

```python
@pytest.mark.skipif(os.environ.get("PREVIEW_MAKER_ENV") != "test", reason="Only run in test environment")
def test_memory_usage():
    """Test that memory usage meets requirements."""
    # Setup
    from memory_profiler import memory_usage
    processor = ImageProcessor()
    test_image_path = "test_data/test_image_12mp.jpg"

    # Measure memory usage
    mem_usage = memory_usage(
        (processor.process_image, (test_image_path,)),
        interval=0.1,
        timeout=10
    )

    # Verification
    assert max(mem_usage) < 250  # Less than 250MB
```

## UI Performance Testing

For UI performance testing, measure frame rates:

```python
@pytest.mark.skipif(os.environ.get("DISPLAY") is None, reason="Requires display")
def test_ui_responsiveness():
    """Test that UI responsiveness meets requirements."""
    # Setup
    window = MainWindow()
    test_image_path = "test_data/test_image.jpg"
    window.load_image(test_image_path)

    # Measure frame rate
    start_time = time.time()
    frame_count = 0

    for _ in range(100):
        # Simulate UI update
        window.update()
        frame_count += 1

    duration = time.time() - start_time
    fps = frame_count / duration

    # Verification
    assert fps > 30  # Greater than 30fps
```

## API Performance Testing

For API performance testing, measure response times:

```python
def test_api_response_time(benchmark):
    """Test that API response time meets requirements."""
    # Setup
    service = GeminiAIService(MockConfig())
    test_image_path = "test_data/test_image.jpg"

    # Benchmark
    result = benchmark(service.analyze_image, test_image_path)

    # Verification
    assert result is not None
    assert benchmark.stats.stats.mean < 0.5  # Less than 500ms
```

## Performance Test Data

Use standardized test data for performance tests:

```python
@pytest.fixture
def performance_test_images():
    """Return a list of test images for performance testing."""
    return [
        "test_data/test_image_1mp.jpg",   # 1 megapixel
        "test_data/test_image_5mp.jpg",   # 5 megapixels
        "test_data/test_image_12mp.jpg",  # 12 megapixels
    ]

def test_image_size_performance(performance_test_images, benchmark):
    """Test that image loading performance scales with image size."""
    # Setup
    processor = ImageProcessor()

    # Test each image size
    results = {}
    for image_path in performance_test_images:
        # Benchmark
        result = benchmark.pedantic(
            processor.process_image,
            args=(image_path,),
            iterations=5,
            rounds=3
        )

        # Store result
        image_size = os.path.basename(image_path).split("_")[2].split(".")[0]
        results[image_size] = benchmark.stats.stats.mean

    # Verification
    assert results["1mp"] < 0.1   # Less than 100ms for 1MP
    assert results["5mp"] < 0.15  # Less than 150ms for 5MP
    assert results["12mp"] < 0.2  # Less than 200ms for 12MP
```

## Performance Test Environment

For consistent performance testing, use a dedicated Docker container:

```bash
# Run performance tests in a dedicated container
docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm \
  --cpuset-cpus="0-1" \
  --memory=1g \
  test pytest tests/performance/
```

## CI/CD Integration

Include performance tests in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run performance tests
  run: docker-compose -f rebuild_plan/docker/docker-compose.yml run --rm test pytest tests/performance/
```

## Performance Regression Testing

For performance regression testing, compare results against baseline:

```python
def test_performance_regression():
    """Test that performance has not regressed."""
    # Setup
    processor = ImageProcessor()
    test_image_path = "test_data/test_image.jpg"

    # Measure performance
    start_time = time.time()
    processor.process_image(test_image_path)
    duration = time.time() - start_time

    # Load baseline
    baseline_path = "tests/performance/baseline.json"
    with open(baseline_path, "r") as f:
        baseline = json.load(f)

    # Verification
    assert duration < baseline["image_processing"] * 1.1  # Allow 10% regression
```