## Code Review Instructions

When performing a code review, apply the following guidelines:

### Python Code Quality
- Verify PEP 8 compliance and consistent code style
- Check for proper type hints on function signatures
- Ensure error handling is appropriate — no bare `except` clauses
- Verify that no sensitive data (tokens, passwords, keys) is hardcoded
- Check for proper use of `with` statements for resource management

### Security (OWASP Top 10)
- Check for injection vulnerabilities (SQL, command, template)
- Verify input validation on all user-facing endpoints
- Ensure no secrets or credentials are committed
- Check for proper authentication and authorization where applicable
- Verify that error responses do not leak internal implementation details

### Testing
- Verify that new or changed code has corresponding test coverage
- Check that tests are meaningful and not just asserting `True`
- Ensure edge cases are tested (empty inputs, boundary values, error conditions)
- Verify that tests can run independently and do not rely on external state

### Docker & Infrastructure
- Check for minimal base images and multi-stage builds where applicable
- Verify that containers run as non-root users
- Ensure no unnecessary ports are exposed
- Check that environment variables are used for configuration, not hardcoded values

### General
- Verify that the PR description clearly explains *what* changed and *why*
- Check that the commit history is clean and logical
- Ensure no unrelated changes are included in the PR
- Verify that documentation is updated if public APIs change
