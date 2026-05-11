# PRD: End-to-End Automated Bug Detection, Verification & Fix Pipeline

## App Overview and Objectives

This project demonstrates an end-to-end automated bug lifecycle on Azure, showcasing GitHub Copilot's capabilities across the entire software development lifecycle. A simple Python web app running on Azure Container Apps intentionally contains a runtime error. When the error occurs:

1. **Detection**: The **Copilot SDK** (Python) catches the error, analyzes it with AI, and automatically opens a GitHub issue with full diagnostic context.
2. **Verification**: A **GitHub Agentic Workflow** triggers on the new issue, using **Copilot CLI** and **Playwright MCP** to reproduce the error in a sandboxed environment, take screenshots, and classify whether the issue is legitimate or a false positive.
3. **Fix**: If verified, the issue is assigned to a **custom coding agent** (`bug-solver`) which fixes the code, runs tests, and opens a PR with screenshots proving the fix.
4. **Review**: The **Copilot Code Review Agent** is assigned to review the PR.
5. **Deploy**: After merge, a **GitHub Actions workflow** (Agentic Workflows) rebuilds and redeploys the container to Azure Container Apps.

### Key Objective
Demonstrate a fully automated feedback loop: **Error → Issue → Verify → Fix → Review → Deploy** — with human oversight at review/merge.

---

## Target Audience

- DevOps/Platform engineers evaluating GitHub Copilot capabilities
- Developer advocates showcasing AI-powered DevOps
- Teams exploring Continuous AI / Agentic Workflows

---

## Architecture Diagram

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Azure Container │     │   GitHub Issues   │     │  Agentic Workflow│
│  Apps (Python)   │────▶│  (auto-created)   │────▶│  (verify-issue)  │
│  + Copilot SDK   │     │  label:needs-     │     │  Copilot CLI +   │
│                  │     │  verification     │     │  Playwright MCP  │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                           │
                              ┌─────────────────┐         │
                              │ Close Issue      │◀── NOT reproducible
                              └─────────────────┘         │
                                                    Reproducible
                                                           │
                              ┌─────────────────┐         ▼
                              │ Custom Agent:    │◀── Assign to
                              │ bug-solver       │    coding agent
                              │ (fix + test +    │
                              │  open PR)        │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ Code Review Agent │
                              │ (@copilot review) │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ Merge PR          │
                              │ (human approval)  │
                              └────────┬─────────┘
                                       │
                              ┌────────▼─────────┐
                              │ Agentic Workflow  │
                              │ (redeploy to ACA) │
                              └──────────────────┘
```

---

## Core Features and Functionality

### 1. Python Web Application with Intentional Runtime Error

**Description**: A Flask web application with a deliberate runtime error that triggers under specific conditions.

**Technical Details**:
- Framework: Flask (lightweight, easy to demo)
- Error type: `ZeroDivisionError` triggered on a specific endpoint (e.g., `/calculate`)
- The app has a healthy homepage (`/`) and a health check endpoint (`/health`)
- The error endpoint simulates a real-world scenario (e.g., division by user input that can be zero)

**Acceptance Criteria**:
- App starts and serves the homepage successfully
- `/health` returns 200 OK
- `/calculate?a=10&b=0` triggers a `ZeroDivisionError`
- Error is caught by the Copilot SDK error handler
- A GitHub issue is automatically created with error details

### 2. Copilot SDK Integration (Error Reporter)

**Description**: Integration of the GitHub Copilot SDK (Python) to detect runtime errors, analyze them with AI, and create GitHub issues.

**Technical Details**:
- Package: `copilot-sdk` (pip)
- The SDK communicates with Copilot CLI via JSON-RPC
- Authentication: `COPILOT_GITHUB_TOKEN` environment variable (PAT with "Copilot Requests" permission)
- Custom tool: `create_github_issue` — allows Copilot to create issues via GitHub API
- Flow:
  1. Flask error handler catches unhandled exceptions
  2. Sends error context (traceback, request info, environment) to Copilot SDK
  3. Copilot analyzes the error and generates a structured issue description
  4. Copilot calls the custom `create_github_issue` tool
  5. Issue is created with label `needs-verification`

**"Draft Issue" Simulation**:
- GitHub API does not support draft issues natively
- We simulate this by creating issues with the label `needs-verification`
- The verification workflow picks up these issues
- If verified → label changes to `verified-bug`
- If not reproducible → issue is closed with explanation

**Environment Variables Required**:
- `COPILOT_GITHUB_TOKEN`: PAT with "Copilot Requests" permission
- `GITHUB_TOKEN`: PAT with `issues:write` permission for creating issues
- `GITHUB_REPO`: Repository in `owner/repo` format

**Acceptance Criteria**:
- Copilot SDK initializes on app startup
- On unhandled exception, Copilot analyzes the error
- A GitHub issue is created with: error type, traceback, request URL, timestamp, environment info
- Issue has label `needs-verification`
- Issue title follows pattern: `[Auto-Bug] <error type>: <brief description>`

### 3. Dockerfile for Containerization

**Description**: Multi-stage Dockerfile for the Python app with Copilot CLI pre-installed.

**Technical Details**:
- Base image: `python:3.12-slim`
- Install Node.js (required for Copilot CLI)
- Install Copilot CLI: `npm install -g @github/copilot`
- Install Python dependencies
- Expose port 8080 (Azure Container Apps default)
- Non-root user for security

**Acceptance Criteria**:
- Image builds successfully
- Container starts and serves the app on port 8080
- Copilot CLI is available inside the container
- Health check passes

### 4. Azure Infrastructure (Bicep)

**Description**: Bicep templates to provision all required Azure resources.

**Resources**:
- Resource Group
- Azure Container Registry (ACR)
- Container App Environment
- Container App
- Log Analytics Workspace (required by Container App Environment)

**Technical Details**:
- Bicep file: `infra/main.bicep`
- Parameters file: `infra/main.bicepparam`
- Pre-deployment script: `scripts/setup-infra.sh` (runs `az deployment` commands)
- Container App configured with:
  - Environment variables for Copilot SDK (from secrets)
  - Ingress enabled on port 8080
  - Min replicas: 1, Max replicas: 1 (demo purposes)
- ACR with admin access enabled for simplicity

**Acceptance Criteria**:
- `scripts/setup-infra.sh` creates all resources successfully
- ACR is accessible and can receive Docker images
- Container App Environment is provisioned
- Container App is configured with correct environment variables

### 5. Deployment Scripts

**Description**: Scripts to build, push, and deploy the container image.

**Scripts**:
- `scripts/setup-infra.sh`: Create Azure infrastructure via Bicep
- `scripts/deploy-app.sh`: Build Docker image, push to ACR, deploy to Container App

**Acceptance Criteria**:
- Scripts are idempotent (can be run multiple times)
- Docker image is built and pushed to ACR
- Container App is updated with new image
- App is accessible via Container App URL

### 6. Issue Verification Workflow (Agentic Workflows)

**Description**: A GitHub Agentic Workflow that triggers when an issue with `needs-verification` label is created. Uses Copilot CLI with Playwright MCP to reproduce the bug in a sandboxed environment.

**Technical Details**:
- Workflow type: Agentic Workflow (`.github/workflows/verify-issue.md`)
- Lock file generated by `gh aw compile`
- Trigger: `issues` event (labeled with `needs-verification`)
- Engine: `copilot` (GitHub Copilot)
- Tools: Shell commands, Playwright MCP
- Safe outputs: `add-comment`, `add-label`, `remove-label`, `close-issue`

**Workflow Logic** (defined in markdown prompt):
1. Read the issue body to extract error details (endpoint, parameters, expected vs actual behavior)
2. Clone the repo and build the Docker container locally
3. Start the container and wait for it to be healthy
4. Use Playwright MCP to navigate to the error endpoint
5. Take screenshots of the error reproduction
6. Analyze the results:
   - If error is reproduced → Add comment with screenshots and analysis, add `verified-bug` label, remove `needs-verification` label
   - If error is NOT reproduced → Add comment explaining why, close the issue
7. If verified, add a comment suggesting to assign to the `bug-solver` agent

**Important Agentic Workflow Constraints**:
- Agent gets read-only GitHub token
- All write operations go through safe outputs
- Agent runs in sandboxed container with network firewall
- Safe outputs are processed by a separate, gated job

**Acceptance Criteria**:
- Workflow triggers on issues with `needs-verification` label
- Copilot CLI successfully builds and runs the container in CI
- Playwright navigates to the error endpoint and captures screenshots
- Screenshots are attached to the issue comment
- Verified issues get `verified-bug` label
- Non-reproducible issues are closed with explanation

### 7. Custom Bug-Solver Agent

**Description**: A custom Copilot coding agent that specializes in fixing bugs identified in issues.

**Technical Details**:
- File: `.github/agents/bug-solver.agent.md`
- YAML frontmatter with `name`, `description`, `tools`
- Prompt instructs the agent to:
  1. Read the issue to understand the bug
  2. Find the relevant code
  3. Fix the bug
  4. Write/update tests to cover the fix
  5. Build and run the app locally to verify
  6. Use Playwright to take "before/after" screenshots
  7. Open a PR with the fix, tests, and screenshots

**Agent Profile**:
```yaml
---
name: bug-solver
description: Specialized agent for diagnosing and fixing runtime bugs. Analyzes issue context, locates root cause, applies fixes, writes tests, and verifies with screenshots.
tools: ["read", "edit", "search", "shell", "write", "playwright-mcp"]
---
```

**Usage**: When a verified issue needs fixing, assign it to Copilot and select the `bug-solver` agent from the dropdown.

**Acceptance Criteria**:
- Agent file is valid and recognized by GitHub
- When assigned to an issue, the agent reads the issue context
- Agent identifies the root cause of the bug
- Agent applies the fix and writes tests
- Agent opens a PR with comprehensive description
- PR includes screenshots demonstrating the fix

### 8. Code Review Agent Instructions

**Description**: Custom instructions for the Copilot Code Review Agent.

**Technical Details**:
- File: `.github/copilot-instructions.md`
- Instructions for code review:
  - Check for proper error handling
  - Verify test coverage
  - Ensure no security vulnerabilities (OWASP top 10)
  - Check Python best practices (PEP 8, type hints)
  - Verify Docker best practices
  - Check for proper logging

**Usage**: After the bug-solver agent opens a PR, request a review from Copilot:
- Via UI: Open PR → Reviewers → Select "Copilot"
- Via CLI: `gh pr edit PR-NUMBER --add-reviewer @copilot`

**Acceptance Criteria**:
- Instructions file is properly formatted
- Copilot Code Review agent follows the custom instructions
- Review comments are relevant and actionable

### 9. Redeployment Workflow (Agentic Workflows)

**Description**: A GitHub Actions workflow that triggers after a PR is merged to `main`, rebuilds the container, and redeploys to Azure Container Apps.

**Technical Details**:
- Workflow file: `.github/workflows/redeploy.md` (Agentic Workflow) + `.github/workflows/redeploy.lock.yml` (compiled)
- Trigger: `push` to `main` branch (after PR merge)
- Steps:
  1. Copilot CLI analyzes what changed in the merge
  2. Builds new Docker image
  3. Pushes to ACR
  4. Updates Container App with new image
  5. Verifies deployment with health check
  6. Creates a summary comment on the merged PR

**Note**: Since redeployment involves secrets (ACR credentials, Azure credentials), the Agentic Workflow will handle the AI analysis part, while a separate standard GitHub Actions job handles the actual deployment with proper secrets access.

**Acceptance Criteria**:
- Workflow triggers on push to main
- Docker image is rebuilt with latest code
- Image is pushed to ACR
- Container App is updated
- Health check confirms deployment success
- Summary is posted

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Application | Python 3.12, Flask |
| AI Integration | Copilot SDK (Python), Copilot CLI |
| Containerization | Docker |
| Cloud Hosting | Azure Container Apps |
| Container Registry | Azure Container Registry (ACR) |
| Infrastructure as Code | Bicep |
| CI/CD | GitHub Actions, Agentic Workflows |
| Browser Automation | Playwright MCP |
| Issue Management | GitHub Issues API |
| Code Review | GitHub Copilot Code Review |
| Coding Agent | GitHub Copilot Coding Agent (custom) |

---

## File Structure

```
ghcp-e2e-demo/
├── PRD.md                                    # This document
├── app/
│   ├── main.py                               # Flask app with intentional bug
│   ├── error_reporter.py                     # Copilot SDK error reporting
│   └── requirements.txt                      # Python dependencies
├── Dockerfile                                # Container image definition
├── infra/
│   ├── main.bicep                            # Azure infrastructure
│   └── main.bicepparam                       # Bicep parameters
├── scripts/
│   ├── setup-infra.sh                        # Create Azure resources
│   └── deploy-app.sh                         # Build & deploy container
├── .github/
│   ├── agents/
│   │   └── bug-solver.agent.md               # Custom bug-fixing agent
│   ├── copilot-instructions.md               # Code Review instructions
│   └── workflows/
│       ├── verify-issue.md                   # Agentic Workflow: verify issues
│       ├── verify-issue.lock.yml             # Compiled workflow (generated by gh aw compile)
│       ├── redeploy.md                       # Agentic Workflow: redeploy on merge
│       └── redeploy.lock.yml                 # Compiled workflow (generated by gh aw compile)
└── tests/
    └── test_app.py                           # Basic tests for the app
```

---

## Security Considerations

1. **Secrets Management**: All tokens (PAT, Azure credentials) stored as GitHub Actions secrets, never in code
2. **Copilot SDK Token**: Requires a PAT with minimal "Copilot Requests" permission
3. **GitHub Token**: Separate PAT with `issues:write` scope for issue creation
4. **Azure Credentials**: Service principal or managed identity for Azure deployments
5. **Agentic Workflows Security**: 5-layer security model (read-only tokens, zero secrets in agent, network firewall, safe outputs, threat detection)
6. **Container Security**: Non-root user, minimal base image, no unnecessary packages

---

## Development Phases

### Phase 1: Foundation (Files 1-5)
- Create Python Flask app with intentional bug
- Implement Copilot SDK error reporter
- Create Dockerfile
- Create Bicep infrastructure templates
- Create deployment scripts

### Phase 2: Automation (Files 6-7)
- Create issue verification Agentic Workflow
- Create custom bug-solver agent

### Phase 3: Review & Deploy (Files 8-9)
- Create Code Review instructions
- Create redeployment Agentic Workflow

### Phase 4: Testing & Demo
- Test end-to-end flow
- Document demo steps

---

## Environment Variables & Secrets

| Variable | Where Used | Description |
|----------|-----------|-------------|
| `COPILOT_GITHUB_TOKEN` | App container, GitHub Actions | PAT with "Copilot Requests" permission |
| `GITHUB_TOKEN` | App container | PAT with `issues:write` for creating issues |
| `GITHUB_REPO` | App container | Repository in `owner/repo` format |
| `AZURE_CREDENTIALS` | GitHub Actions | Azure service principal JSON |
| `ACR_NAME` | GitHub Actions, deploy script | Azure Container Registry name |
| `RESOURCE_GROUP` | GitHub Actions, deploy script | Azure resource group name |
| `CONTAINER_APP_NAME` | GitHub Actions, deploy script | Azure Container App name |
| `PERSONAL_ACCESS_TOKEN` | GitHub Actions | PAT for Copilot CLI authentication |

---

## Prerequisites for Demo

1. **GitHub Account** with Copilot Pro/Pro+ or Business/Enterprise plan
2. **Azure Subscription** with permissions to create resources
3. **GitHub CLI** (`gh`) installed with `gh-aw` extension
4. **Azure CLI** (`az`) installed and authenticated
5. **Docker** installed locally for building images
6. **Node.js 18+** (for Copilot CLI)
7. **PAT Tokens**: One with "Copilot Requests" permission, one with `repo` scope

---

## Potential Challenges and Solutions

| Challenge | Solution |
|-----------|---------|
| Copilot SDK requires CLI authentication in container | Pass `COPILOT_GITHUB_TOKEN` env var |
| No native "draft issues" in GitHub API | Simulate with `needs-verification` label |
| Agentic Workflows are read-only | Use safe outputs for all write operations |
| Playwright in CI needs browser installed | Use `npx playwright install` in workflow |
| ACR authentication from Container Apps | Use managed identity or admin credentials |
| Copilot CLI rate limits | Add retry logic and exponential backoff |

---

## Demo Steps (End-to-End)

1. **Deploy**: Run `scripts/setup-infra.sh` then `scripts/deploy-app.sh`
2. **Trigger Error**: Visit `https://<app-url>/calculate?a=10&b=0`
3. **Observe Issue Creation**: Check GitHub Issues — auto-created with `needs-verification` label
4. **Watch Verification**: Agentic Workflow runs, reproduces error, adds screenshots, labels as `verified-bug`
5. **Assign Bug-Solver**: Assign the issue to Copilot, select `bug-solver` agent
6. **Watch Fix**: Bug-solver agent analyzes, fixes, tests, and opens PR
7. **Code Review**: Assign Copilot as reviewer on the PR
8. **Merge**: Review and merge the PR
9. **Watch Redeploy**: Redeployment workflow rebuilds and deploys
10. **Verify Fix**: Visit `https://<app-url>/calculate?a=10&b=0` — no longer crashes
