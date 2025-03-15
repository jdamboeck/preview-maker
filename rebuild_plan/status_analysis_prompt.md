# Preview Maker Rebuild Status Analysis Agent Prompt

## Task Overview
You will analyze the current status of the Preview Maker rebuild project, update documentation where needed, perform quality checks on implemented components, and formulate a plan for the next development task.

## Step 1: Current Status Analysis

### Repository Analysis
1. Analyze the git commit history to understand recent changes:
   ```bash
   git log --oneline -n 10
   ```
2. Check branch status:
   ```bash
   git branch -a
   ```
3. Check any uncommitted changes:
   ```bash
   git status
   ```

### Progress Tracking Analysis
1. Review `/home/jd/dev/projects/preview-maker/rebuild_plan/progress_tracking.md`
2. Identify:
   - Completed components and milestones
   - In-progress components
   - Next components according to dependency order
   - Any blockers or issues documented

### Component Status Analysis
1. Compare the actual implementation status with the progress tracking document
2. For each component marked as "Completed" or "In Progress", verify:
   - Existence of corresponding files
   - Test coverage
   - Documentation status

### File Structure Analysis
1. Check if the actual file structure aligns with the planned structure in:
   - `/home/jd/dev/projects/preview-maker/rebuild_plan/04_file_structure/01_directory_structure.md`
2. Identify any structural gaps or inconsistencies

## Step 2: Documentation Updates

Update any inconsistencies in documentation based on the actual project status:

1. Progress Tracking Document:
   - Update component statuses (Not Started, In Progress, In Review, Completed, Blocked)
   - Update documentation status
   - Update testing progress
   - Update milestone dates if applicable

2. README.md:
   - Ensure it accurately reflects current project state
   - Update any changed commands or workflows

3. Component Documentation:
   - For any completed components not properly documented, add or update documentation

## Step 3: Quality Review

For implemented components, perform these quality checks:

1. **Code Structure Check**:
   - Verify components follow the component-based architecture
   - Check for proper separation of concerns
   - Verify dependency flow (dependencies flow inward)

2. **Testing Check**:
   - Verify unit tests exist for completed components
   - Ensure tests can run in the Docker environment
   - Check for integration tests for component interactions

3. **Documentation Check**:
   - Verify docstrings exist for all public functions and classes
   - Ensure README.md is up to date
   - Check that architecture documentation reflects actual implementation

4. **Docker Environment Check**:
   - Verify Docker setup works for all implemented components
   - Check that tests can run in Docker environment

## Step 4: Next Task Planning

Based on the progress tracking and component dependencies, identify the next highest-priority task:

1. Review the implementation sequence in:
   - `/home/jd/dev/projects/preview-maker/rebuild_plan/06_implementation_strategy/01_implementation_sequence.md`

2. Consider component dependencies in:
   - `/home/jd/dev/projects/preview-maker/rebuild_plan/00_prerequisites/08_component_dependency_diagram.md`

3. Formulate a detailed plan for implementing the next component, including:

```markdown
# Preview Maker Rebuild Project - Next Task Implementation Plan

## Core Functionality
[Describe the specific component or feature to be implemented and its relation to the overall functionality]

## Technical Requirements
[List the specific technical requirements for this component]

## Docker Development Environment
[Specify any specific Docker commands needed for developing and testing this component]

## Technical Specifications
[Provide detailed specifications for this component, including performance targets, error handling, etc.]

## Key Development Resources
[List specific resources relevant to this component]

## Implementation Patterns
[Describe specific implementation patterns to use for this component]

## Development Plan
1. **Setup and Preparation**
   - [Specific preparation steps]

2. **Test Creation**
   - [Specific tests to create first]

3. **Component Implementation**
   - [Step-by-step implementation plan]

4. **Integration**
   - [How to integrate with existing components]

5. **Documentation**
   - [Documentation requirements]

## Debugging Approach
[Specific debugging strategies for this component]

## Testing Strategy
[Detailed testing plan for this component]
```

## Step 5: Output Format

1. Provide a detailed status report of the current project state
2. List any documentation updates you've made
3. Present your quality review findings
4. Provide your complete implementation plan for the next task

## Reference Materials
- agent_shortterm_memory.md for development cycle overview
- progress_tracking.md for current component status
- git_workflow.md for contribution guidelines
- starter_prompt.md for template structure
- quick_reference.md for common operations
- architecture/06_technical_specifications.md for technical details
- 00_prerequisites/08_component_dependency_diagram.md for component dependencies
- 06_implementation_strategy/01_implementation_sequence.md for implementation order