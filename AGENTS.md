# Repository Guidelines

## Primary Directive

- Think in English, interact with the user in Japanese.
- When modifying the implementation, strictly adhere to the t-wada style of Test-Driven Development (TDD).
  - **t-wada TDD Concept**:
    1. 1st Issue
        1. First, write a failing test (Red).
            - make test
            - make check-all
        2. Then, write the simplest code to make it pass (Green).
            - make test-cov
            - make check-all
        3. Finally, refactor the code (Refactor).
    2. 2nd Issue
        1. First, write a failing test (Red).
            - make test
            - make check-all
        2. Then, write the simplest code to make it pass (Green).
            - make test-cov
            - make check-all
        3. Finally, refactor the code (Refactor).
  - Each cycle should be small and focused on a single purpose.

## Project Structure & Module Organization
- Core plugin code lives in `src/mkdocs_svg_to_png/` (e.g., `plugin.py`, `svg_converter.py`, `utils.py`).
- Tests are under `tests/`, with unit specs in `tests/unit/` and shared fixtures in `tests/conftest.py`.
- Documentation sources sit in `docs/`; built MkDocs output appears in `site/`.
- Helper scripts reside in `scripts/`, and automation targets are defined in the `Makefile`.

## Build, Test, and Development Commands
- `make install-dev`: install the package in editable mode via `uv`.
- `make test` / `make test-unit`: run the full Pytest suite or only unit tests.
- `make test-cov`: execute Pytest with coverage reports (`htmlcov/` output).
- `make format`, `make lint`, `make typecheck`: apply Ruff formatting, run Ruff linting with fixes, and run strict mypy.
- `make serve` / `make build`: serve or build the MkDocs documentation (`ENABLE_PDF_EXPORT=1 make build-pdf` enables PDF output).

## Coding Style & Naming Conventions
- Python code uses 4-space indentation and follows an 88-character line limit (configured in `pyproject.toml`).
- Ruff enforces linting (`E`, `W`, `F`, `B`, `SIM`, etc.); run `make check` before pushing.
- Maintain type hints—mypy runs in `strict` mode for `src/`, while tests may use looser typing per overrides.
- Module filenames are snake_case; exported classes (e.g., `SvgToPngPlugin`) use PascalCase.

## Testing Guidelines
- Tests use Pytest; match the naming patterns in `pyproject.toml` (`test_*.py`, `*_test.py`).
- Prefer `tests/unit/` for fast, isolated checks; place heavier integration work under a matching subfolder.
- Mock Playwright interactions (e.g., `_run_playwright_conversion`) instead of launching browsers in unit tests.
- Generate coverage with `make test-cov` and review `htmlcov/index.html` before major submissions.

## Commit & Pull Request Guidelines
- Follow the observed Conventional Commit prefixes (`fix:`, `feat:`, `docs:`, `refactor:`). Combine scopes cautiously, as in `fix: ... docs: ...`.
- Squash noisy WIP history locally; commits should narrate intent and impact.
- PRs should include: summary of changes, testing evidence (command output or coverage note), any relevant `TODO.md` updates, and linked issues.
- Ensure `make check` and `make test` pass before requesting review; attach screenshots for documentation-facing changes when practical.
