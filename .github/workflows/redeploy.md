---
description: >
  Agentic workflow that rebuilds and redeploys the application to Azure
  Container Apps after a PR is merged to the main branch. Uses Copilot CLI
  to analyze changes and generate a deployment summary.

name: Redeploy on Merge

on:
  push:
    branches: [main]
    paths:
      - 'app/**'
      - 'Dockerfile'
      - 'infra/**'

permissions:
  contents: read
  pull-requests: read
  issues: read

engine: copilot

tools:
  bash:
    - git:*
    - cat:*

safe-outputs:
  create-issue:
    title-prefix: "[Deploy] "
    labels: [deployment, automated]
    max: 1

timeout-minutes: 10
---

# Deployment Analyzer

You are a deployment analyst. A PR was just merged to the main branch.
Your job is to analyze what changed and create a deployment summary issue.

## Steps

### 1. Analyze Recent Changes

Review the most recent merge commit to understand what changed:

```bash
git log --oneline -5
git diff HEAD~1 --stat
git diff HEAD~1 -- app/ Dockerfile
```

### 2. Assess Deployment Impact

Determine:
- What files changed (app code, Dockerfile, infrastructure, tests)
- Whether the changes require a container rebuild
- Any potential risks or breaking changes
- Whether database migrations or config changes are needed

### 3. Create Deployment Summary

Create a GitHub issue summarizing:
- What changed in this merge
- The deployment steps that should be executed
- Any risks or manual steps required
- A checklist for the deployment

Use the `[Deploy]` title prefix.

The actual deployment (Docker build, ACR push, Container App update) will be
handled by the companion CI/CD job in the lock file that has access to
Azure credentials.
