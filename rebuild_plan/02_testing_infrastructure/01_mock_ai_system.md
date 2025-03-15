# Phase 2.1: Mock System for AI Services

## Overview
This phase creates a robust mocking system for AI services to ensure that testing can be performed reliably without depending on external API access. This is essential for consistent testing, CI/CD integration, and development without API costs.

## Goals
- Create a mock framework for Gemini AI responses
- Build utilities to record and replay real API responses for testing
- Implement environment detection for test vs. production
- Add a toggleable AI service availability simulation

## Tasks

### Task 2.1.1: Design Mock AI Service Architecture
- [ ] Define interface for AI service abstraction
- [ ] Create mock response data structure
- [ ] Design response matching algorithm based on image characteristics
- [ ] Create environment detection mechanism

**Success Criteria**: Architecture document for mock system with clear interfaces and data flow diagrams

### Task 2.1.2: Create Mock Gemini Response Storage
- [ ] Create directory structure for mock responses
  ```bash
  mkdir -p tests/mocks/gemini_responses
  ```
- [ ] Define JSON schema for storing responses
  ```bash
  touch tests/mocks/response_schema.json
  ```
- [ ] Create sample response files for common test cases
  ```bash
  touch tests/mocks/gemini_responses/sample_detail.json
  touch tests/mocks/gemini_responses/sample_product.json
  touch tests/mocks/gemini_responses/sample_error.json
  ```
- [ ] Add metadata for matching responses to queries

**Success Criteria**: Mock response storage system with well-defined schema and sample responses

### Task 2.1.3: Implement Mock AI Service
- [ ] Create base mock service class
  ```bash
  touch app/core/ai_service_base.py
  touch tests/mocks/mock_gemini_service.py
  ```
- [ ] Implement methods to load and match mock responses
- [ ] Add toggleable availability simulation
- [ ] Implement response simulation with configurable delay

**Success Criteria**: Working mock service that can be used to simulate AI responses

### Task 2.1.4: Create Response Recording Utility
- [ ] Implement a utility to capture real API responses
  ```bash
  touch tools/record_ai_responses.py
  ```
- [ ] Create mechanism to store responses with their input parameters
- [ ] Add anonymization option for sensitive data
- [ ] Create conversion utility to transform responses to mock format

**Success Criteria**: Utility successfully records and formats real API interactions for testing

## AI Entry Point
When entering at this step, you should:

1. Examine the current AI service implementation in the codebase
   - Look particularly at `src/gemini_analyzer.py`
   - Understand the interface and response format
2. Study the prompt files in the `prompts/` directory
3. Design the mock system architecture as in Task 2.1.1
   - Focus on making it a drop-in replacement for the real service
4. Create the mock response storage structure as in Task 2.1.2
5. Implement the mock service as in Task 2.1.3
   - Ensure it mimics all behaviors of the real service
   - Add toggleable failure modes for testing error handling
6. Develop the recording utility as in Task 2.1.4
7. Verify all success criteria are met
8. Proceed to Phase 2.2: Testing Framework Setup

## Next Steps
Once this phase is complete, proceed to [Testing Framework Setup](./02_testing_framework.md)