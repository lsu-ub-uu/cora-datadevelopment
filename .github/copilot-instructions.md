# Repository Instructions

- This is a Python 3.14 project. Use Python for changes unless a task explicitly requires another language.
- Target Pylance `strict` type checking for Python code. Add accurate annotations and resolve relevant strict-mode diagnostics in changed code.
- Follow Clean Code and SOLID principles where they improve clarity and maintainability. Prefer small, focused changes and established repository patterns over speculative abstractions.
- Use a test-first workflow: add or update focused tests for behavior changes, then run the relevant tests. Aim for complete coverage of changed behavior without adding brittle or redundant tests.
- Run the project test suite with `pytest`; use `pytest --cov=src` when coverage is relevant.
- Keep changes within the requested scope. Do not modify migration data, generated files, credentials, or unrelated behavior unless the task requires it.
- Follow the migration and operational guidance in `README.md` and the relevant file under `docs/` when changing a script or workflow.
- Preserve existing public interfaces and conventions unless the request requires a change.