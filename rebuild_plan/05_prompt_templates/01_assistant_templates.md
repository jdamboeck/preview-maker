# Phase 5.1: Create AI Assistant Prompt Templates

## Overview
This phase develops comprehensive prompt templates that will guide AI assistants in working with the codebase. These templates provide context about the application architecture, coding standards, and component relationships to maximize AI effectiveness in the rebuild process.

## Goals
- Develop comprehensive prompt templates for AI assistants
- Create context documentation about the application architecture
- Set up role-specific instructions for different coding tasks
- Include navigation aids for the codebase

## Tasks

### Task 5.1.1: Create Base AI Assistant Template
- [ ] Design main AI assistant prompt structure
  ```bash
  touch docs/ai/base_assistant_template.md
  ```
- [ ] Document application architecture for AI context
  ```bash
  touch docs/ai/architecture_summary.md
  ```
- [ ] Create codebase navigation guide
  ```bash
  touch docs/ai/codebase_navigation.md
  ```
- [ ] Establish coding standards summary for AI
  ```bash
  touch docs/ai/coding_standards_summary.md
  ```

**Success Criteria**: Complete base template that provides all necessary context for an AI assistant

### Task 5.1.2: Create Task-Specific Templates
- [ ] Develop implementation task template
  ```bash
  touch docs/ai/templates/implementation_task.md
  ```
- [ ] Create bug fixing task template
  ```bash
  touch docs/ai/templates/bug_fix_task.md
  ```
- [ ] Design feature enhancement template
  ```bash
  touch docs/ai/templates/enhancement_task.md
  ```
- [ ] Establish refactoring task template
  ```bash
  touch docs/ai/templates/refactoring_task.md
  ```

**Success Criteria**: Set of specialized templates for common development tasks

### Task 5.1.3: Create Component-Specific Context
- [ ] Develop core module context document
  ```bash
  touch docs/ai/context/core_modules.md
  ```
- [ ] Create UI module context document
  ```bash
  touch docs/ai/context/ui_modules.md
  ```
- [ ] Design utility module context document
  ```bash
  touch docs/ai/context/utility_modules.md
  ```
- [ ] Establish configuration context document
  ```bash
  touch docs/ai/context/configuration.md
  ```

**Success Criteria**: Component-specific context documents that provide detailed information about each area

### Task 5.1.4: Create AI Interaction Examples
- [ ] Develop implementation example
  ```bash
  touch docs/ai/examples/implementation_example.md
  ```
- [ ] Create bug fixing example
  ```bash
  touch docs/ai/examples/bug_fix_example.md
  ```
- [ ] Design feature enhancement example
  ```bash
  touch docs/ai/examples/enhancement_example.md
  ```
- [ ] Establish common pitfalls document
  ```bash
  touch docs/ai/examples/common_pitfalls.md
  ```

**Success Criteria**: Clear examples demonstrating effective AI interactions for different tasks

### Task 5.1.5: Create Cursor-Specific Guidelines
- [ ] Update .cursorrules file with project-specific guidelines
  ```bash
  # Update existing file:
  # .cursorrules
  ```
- [ ] Create Cursor-specific command templates
  ```bash
  touch docs/ai/cursor_commands.md
  ```
- [ ] Document environment setup for Cursor
  ```bash
  touch docs/ai/cursor_environment.md
  ```
- [ ] Establish best practices for Cursor interactions
  ```bash
  touch docs/ai/cursor_best_practices.md
  ```

**Success Criteria**: Complete set of Cursor-specific guidelines optimized for the project

## AI Entry Point
When entering at this step, you should:

1. First examine the existing codebase to understand its structure and purpose
2. Review the documentation created in previous phases, especially:
   - The code standards document
   - Component specifications
   - Directory structure
3. Create the base AI assistant template as in Task 5.1.1
   - Include comprehensive overview of the application
   - Document the component architecture
   - Provide navigation guidance for the codebase
4. Develop task-specific templates as in Task 5.1.2
   - Create templates for common development tasks
   - Include guidance specific to each task type
5. Create component-specific context as in Task 5.1.3
   - Document each major component area
   - Explain component relationships and interfaces
6. Develop AI interaction examples as in Task 5.1.4
   - Provide concrete examples of successful AI interactions
   - Highlight common pitfalls and how to avoid them
7. Create Cursor-specific guidelines as in Task 5.1.5
   - Update .cursorrules for the project
   - Document Cursor-specific command templates
8. Verify all success criteria are met
9. Proceed to Phase 5.2: Develop Agent Workflow Documentation

## Next Steps
Once this phase is complete, proceed to [Develop Agent Workflow Documentation](./02_workflow_documentation.md)