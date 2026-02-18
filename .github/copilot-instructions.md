# AI Assistant Coding Guide for PromptLab

This file tells AI coding assistants how to work in this project. Keep changes narrow, align with the existing FastAPI + Pydantic style, and avoid drive-by refactors.

## Project Coding Standards
- Target Python 3.10; use type hints everywhere.
- Prefer small, pure helpers in `app/utils.py`; keep storage logic in `app/storage.py`.
- Use Pydantic models for request/response validation; keep schema definitions in `app/models.py`.
- Maintain Google-style docstrings on public functions/classes: include description, Args (with types and concise descriptions), Returns, Raises, and an Example usage block; add brief inline comments only when logic is non-obvious.
- Preserve existing behaviors unless a spec explicitly changes them.

## Preferred Patterns and Conventions
- FastAPI routes live in `app/api.py` with `response_model` set; use `HTTPException` for user-facing errors.
- IDs are UUID strings via `generate_id`; timestamps via `get_current_time` (UTC).
- Prompt listing flow: pull all prompts → apply collection filter → apply search → sort newest-first (`sort_prompts_by_date(descending=True)`).
- Storage stays in-memory (`Storage` class); mutate through its methods, not raw dicts.
- Follow specs in `specs/` for tagging, prompt versioning, and future features; keep defaults: AND tag filtering, newest-first sorting, sequential version numbers.
- Keep CORS permissive as currently configured; do not tighten without product ask.
- No new dependencies unless justified and pinned in `backend/requirements.txt`.

## File Naming Conventions
- Python modules: `snake_case.py`; tests: `test_*.py` under `backend/tests/`.
- Fixtures belong in `backend/tests/conftest.py`; add new sample data fixtures there.
- Documentation/specs: place new design docs in `docs/` or `specs/` with clear titles.

## Error Handling Approach
- Use `fastapi.HTTPException` with precise status codes: `404` for missing resources, `400` for bad input/invalid references, `409` for conflict/no-op protections, `500` only for unexpected errors.
- Validate related resources before acting (e.g., ensure `collection_id` exists before attaching).
- Avoid bare `except`; handle known failure modes explicitly and re-raise with clear `detail`.
- Keep responses deterministic; do not leak stack traces or internal data to clients.

## Testing Requirements
- Add or update pytest coverage in `backend/tests/` for any behavior change or new endpoint.
- Use `fastapi.testclient.TestClient`; rely on `storage.clear()` fixtures to isolate tests.
- Cover success and error paths (missing IDs, bad payloads, conflict cases).
- Run `pytest tests/ -v` from `backend/` before submitting; if not run, state why and what to verify.
