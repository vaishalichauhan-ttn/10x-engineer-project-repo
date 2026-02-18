## Tagging System

### Overview
- Introduce reusable tags that can be attached to prompts for organization and discovery.
- Tags are global (shared across prompts) and many-to-many with prompts.
- Search/filter extends existing `/prompts` query parameters to include tags while preserving collection and text search behavior.

### User Stories & Acceptance Criteria
- Editor creates and manages tags.
  - AC: `POST /tags` creates a tag with unique `name` (case-insensitive), returns 200 with metadata.
  - AC: `DELETE /tags/{tag_id}` removes the tag and detaches it from all prompts.
- Editor assigns/unassigns tags to a prompt.
  - AC: `POST /prompts/{prompt_id}/tags` supports batch assign; returns updated prompt with tag ids.
  - AC: `DELETE /prompts/{prompt_id}/tags/{tag_id}` removes one tag; 404 if prompt or tag missing.
- Editor filters prompts by tags.
  - AC: `GET /prompts?tags=tag1,tag2` returns prompts that contain all requested tags (AND by default).
  - AC: Tag filtering works together with existing `collection_id` and `search` parameters.
- Editor views tags on a prompt.
  - AC: `GET /prompts/{prompt_id}` includes `tags` array (ids and names) if tags exist.
- Editor lists all tags.
  - AC: `GET /tags` lists tags with prompt usage counts.

### Data Model Changes
- New model `Tag`:
  - `id` (uuid), `name` (unique, lowercased for comparisons), `description` (optional), `created_at`.
- New join model `PromptTag` (may be implicit in storage):
  - `prompt_id`, `tag_id`, `attached_at`.
- Prompt model extension:
  - Add `tags: List[str] = []` (store tag ids on prompt) for lightweight retrieval; when returning prompts, enrich with tag names via lookup.
- Storage additions:
  - CRUD for tags; maintain mapping prompt_id → tag_ids and tag_id → prompt_ids.
  - Helper to enforce tag name uniqueness (case-insensitive).

### API Specifications
- `GET /tags`
  - Returns list of tags with optional usage count (`prompt_count`).
- `POST /tags`
  - Body: `name` (required), `description` (optional).
  - Responses: 200 with tag; 400 on duplicate name.
- `DELETE /tags/{tag_id}`
  - Detaches tag from prompts, then deletes tag; 404 if missing.
- `POST /prompts/{prompt_id}/tags`
  - Body: `tag_ids` (list of tag ids).
  - Behavior: attaches all provided tags, ignores already-attached, 400 if any tag id invalid, 404 if prompt missing.
  - Response: updated prompt with tags.
- `DELETE /prompts/{prompt_id}/tags/{tag_id}`
  - Detaches one tag; 404 if prompt or tag missing.
- Prompt retrieval/listing changes:
  - `GET /prompts` accepts `tags` query param (comma-separated ids or names). Default behavior: AND match; consider `match=any` for OR as optional extension.
  - `GET /prompts/{prompt_id}` returns prompt with resolved tag metadata.

### Search & Filter Requirements
- Combine filters: tags AND collection AND text search should all apply together.
- Default tag filter mode: AND (prompt must include all specified tags).
- Optional extension: `match=any` to switch to OR.
- Performance (in-memory): use set intersection on prompt tag ids; keep tag name → id map for case-insensitive lookup.
- Sorting: preserve existing `sort_prompts_by_date(descending=True)` after filtering.
