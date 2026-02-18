## Prompt Version Tracking

### Overview
- Add first-class version history for prompts so editors can track changes, compare revisions, and roll back when necessary.
- Versions are immutable snapshots taken on create/update operations (PUT/PATCH).
- Stored alongside prompts (in-memory for now) with clear linkage to the source prompt.

### User Stories & Acceptance Criteria
- Editor saves a new version automatically whenever a prompt is updated.
  - AC: Any PUT/PATCH on an existing prompt records a new version with `version_number`, `created_at`, and the full prompt payload.
  - AC: Version numbering is sequential per prompt starting at 1.
- Editor views version history for a prompt.
  - AC: `GET /prompts/{prompt_id}/versions` returns list newest-first with metadata and minimal prompt info.
- Editor inspects a specific version.
  - AC: `GET /prompts/{prompt_id}/versions/{version_number}` returns the full snapshot.
- Editor reverts a prompt to a prior version.
  - AC: `POST /prompts/{prompt_id}/versions/{version_number}/revert` replaces the current prompt fields with that snapshot, bumps `updated_at`, and creates a new version capturing the revert action.
- Editor adds a manual checkpoint without modifying the prompt.
  - AC: `POST /prompts/{prompt_id}/versions` allows optional `note` and captures the current prompt as a new version without changing the prompt content.

### Data Model Changes
- New model `PromptVersion`:
  - `id` (uuid), `prompt_id` (fk), `version_number` (int, per-prompt sequence), `title`, `content`, `description`, `collection_id`, `created_at`, `created_by` (optional future), `note` (optional).
- Prompt keeps existing shape; no schema change required for prompts themselves.
- Storage additions:
  - Per-prompt version list, sorted newest-first.
  - Helper to compute next `version_number`.
  - Retrieval by `(prompt_id, version_number)`.

### API Specifications
- `GET /prompts/{prompt_id}/versions`
  - Params: optional `limit`, `offset`.
  - Responses: 200 with list of versions (metadata + selected fields), 404 if prompt missing.
- `GET /prompts/{prompt_id}/versions/{version_number}`
  - Responses: 200 with full snapshot, 404 if prompt or version missing.
- `POST /prompts/{prompt_id}/versions`
  - Purpose: manual checkpoint.
  - Body: optional `note`.
  - Responses: 201 with new version, 404 if prompt missing.
- `POST /prompts/{prompt_id}/versions/{version_number}/revert`
  - Purpose: restore a prior version.
  - Responses: 200 with updated prompt and newly created version entry; 404 if prompt/version missing; 409 if current prompt already matches target version (no-op safeguard).
- Side effect on existing endpoints:
  - `PUT /prompts/{prompt_id}` and `PATCH /prompts/{prompt_id}` create a new version after successful update (include post-update state).

### Edge Cases
- Prompt not found → 404 for all version routes.
- Version not found → 404.
- No-op revert (content identical) → 409 or 200 with `reverted=false` (choose one consistently; recommended 409 to signal no change).
- Deleting prompts: delete all versions when prompt is deleted.
- Collection deletion: versions should preserve historical `collection_id` even if the collection was removed later.
- Large histories: introduce optional pagination; default limit (e.g., 50) - later.
