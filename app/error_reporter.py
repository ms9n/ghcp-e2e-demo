import asyncio
import json
import os
import traceback
from datetime import datetime, timezone

import requests
from copilot import CopilotClient
from copilot.tools import define_tool
from pydantic import BaseModel, Field


class CreateIssueParams(BaseModel):
    title: str = Field(description="Title for the GitHub issue")
    body: str = Field(description="Markdown body for the GitHub issue")
    labels: list[str] = Field(
        default=["needs-verification", "auto-bug"],
        description="Labels to apply to the issue",
    )


GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _create_github_issue(title: str, body: str, labels: list[str]) -> dict:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": title, "body": body, "labels": labels}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


@define_tool(
    name="create_github_issue",
    description="Creates a GitHub issue to report a detected runtime error. Use this when you have analyzed an error and want to file a bug report.",
    skip_permission=True,
)
def create_issue_tool(params: CreateIssueParams) -> str:
    result = _create_github_issue(params.title, params.body, params.labels)
    return json.dumps(
        {
            "issue_number": result["number"],
            "url": result["html_url"],
            "state": result["state"],
        }
    )


async def report_error(error: Exception, request_context: dict | None = None) -> None:
    if not GITHUB_REPO or not GITHUB_TOKEN:
        print("[error_reporter] GITHUB_REPO or GITHUB_TOKEN not set, skipping report")
        return

    tb = traceback.format_exception(type(error), error, error.__traceback__)
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": "".join(tb),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": request_context or {},
    }

    prompt = f"""A runtime error occurred in a production Python web application.
Analyze this error and create a GitHub issue with a clear title and detailed body.

Error details:
```json
{json.dumps(error_info, indent=2)}
```

Requirements for the issue:
- Title must start with "[Auto-Bug]" followed by the error type and a brief description
- Body must use the following markdown template with these exact section headers:

## Error Summary
Brief description of the error.

## Reproduction Steps
1. Start the application
2. [Exact HTTP method and URL with parameters that triggered the error]
3. Observe the error response

**HTTP Method:** `[METHOD]`
**Endpoint:** `[path with query parameters]`
**Request Body:** [body if applicable, or "N/A"]

## Error Details
- **Type:** `[error type]`
- **Message:** [error message]
- **Timestamp:** [ISO timestamp]

## Traceback
```
[full traceback]
```

## Request Context
```json
[request context JSON]
```

## Root Cause Analysis
[Your analysis of the likely root cause]

- Always include the labels: ["needs-verification", "auto-bug"]

Create the issue now using the create_github_issue tool."""

    async with CopilotClient() as client:
        session = await client.create_session(
            model="claude-opus-4-6",
            tools=[create_issue_tool],
            on_permission_request=lambda _: {"kind": "approved"},
        )
        await session.send_and_wait(prompt=prompt)


def report_error_sync(error: Exception, request_context: dict | None = None) -> None:
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(report_error(error, request_context))
        loop.close()
    except Exception as e:
        print(f"[error_reporter] Failed to report error: {e}")
