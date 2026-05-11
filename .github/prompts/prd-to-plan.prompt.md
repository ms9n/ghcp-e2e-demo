---
name: prd-to-plan
description: Convert PRD to a structured plan.md file using Anthropic's recommended task harness format
---

# PRD to Plan Converter

Convert the PRD.md file into a structured `plan.md` file following Anthropic's recommended format for effective long-running agent harnesses.

## Instructions

1. Enrich your context by reading the following article: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
2. Read and analyze the `PRD.md` file in the current workspace
3. Extract all features, requirements, and milestones
4. Generate a `plan.md` file with the structure below

## Output Format

The plan.md file MUST follow this exact structure:

```markdown
# Project Plan

## Overview
[Brief 2-3 sentence description of what the project is building, extracted from the PRD]

**Reference:** `PRD.md`

---

## Task List

\`\`\`json
[
  {
    "category": "setup",
    "description": "[Task description]",
    "steps": [
      "[Specific actionable step 1]",
      "[Specific actionable step 2]"
    ],
    "passes": false
  }
]
\`\`\`
```

## Task Categories

Use these categories to organize tasks:

- **setup**: Project initialization, configuration, dependency installation
- **feature**: Feature implementation tasks
- **ui**: UI/styling/component tasks
- **integration**: API integration, data flow, service connections
- **testing**: Testing, validation, QA tasks
- **documentation**: Documentation, README, comments

## Guidelines for Creating Tasks

1. **Break down by feature/milestone**: Each major feature or PRD section should become one or more tasks
2. **Actionable steps**: Each step should be a concrete, completable action (not vague descriptions)
3. **Logical order**: Tasks should be ordered by dependency (setup first, then features, then polish)
4. **Granularity**: Steps should be small enough to complete in one focused session
5. **Verifiable**: Each step should have a clear "done" state
6. **All passes start as false**: The `passes` field tracks completion status

## Example Task Breakdown

For a PRD with authentication and dashboard features:

```json
[
  {
    "category": "setup",
    "description": "Initialize project structure and core dependencies",
    "steps": [
      "Create Vite + React project with TypeScript",
      "Install routing dependencies (react-router-dom)",
      "Install UI dependencies (tailwindcss, lucide-react)",
      "Configure Tailwind CSS",
      "Set up project folder structure",
      "Verify dev server runs successfully"
    ],
    "passes": false
  },
  {
    "category": "setup",
    "description": "Set up state management and API configuration",
    "steps": [
      "Create context providers for app state",
      "Set up environment variables for API keys",
      "Create API service layer with axios",
      "Implement basic caching utility"
    ],
    "passes": false
  },
  {
    "category": "feature",
    "description": "Implement authentication page",
    "steps": [
      "Create AuthPage component",
      "Build login form with username/password fields",
      "Add form validation (non-empty fields)",
      "Implement auth context for session state",
      "Add redirect to home on successful login"
    ],
    "passes": false
  }
]
```

## Now Convert the PRD

Read the PRD.md file and generate a comprehensive plan.md file following this format. Ensure:

- Every major feature from the PRD has corresponding tasks
- Setup tasks come first
- Tasks follow the development phases/milestones if specified in the PRD
- Steps are specific and actionable, not generic
- The overview accurately summarizes the project