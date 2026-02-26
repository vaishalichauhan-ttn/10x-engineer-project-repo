"""API tests for PromptLab."""

import time
from fastapi.testclient import TestClient


class TestHealth:
    """Tests for health endpoint."""

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPrompts:
    """Tests for prompt endpoints."""

    def test_create_prompt(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_prompt_with_invalid_collection_returns_400(
        self, client: TestClient, sample_prompt_data
    ):
        response = client.post(
            "/prompts",
            json={**sample_prompt_data, "collection_id": "does-not-exist"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_create_prompt_empty_title_returns_422(self, client: TestClient):
        response = client.post("/prompts", json={"title": "", "content": "valid content"})
        assert response.status_code == 422

    def test_create_prompt_empty_content_returns_422(self, client: TestClient):
        response = client.post("/prompts", json={"title": "Valid", "content": ""})
        assert response.status_code == 422

    def test_create_prompt_special_characters(self, client: TestClient):
        special_payload = {
            "title": "Spec!@#$%^&*()_+-=[]{}|;':,.<>/?`~",
            "content": "Line1\nLine2 with emoji-like text :rocket: and symbols <> {} []",
            "description": "Description with \n new lines and punctuation!!!",
        }
        response = client.post("/prompts", json=special_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == special_payload["title"]
        assert data["content"] == special_payload["content"]

    def test_list_prompts_empty(self, client: TestClient):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0

    def test_list_prompts_with_data(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        client.post("/prompts", json=sample_prompt_data)
        
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert len(data["prompts"]) == 1
        assert data["total"] == 1

    def test_get_prompt_success(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.get(f"/prompts/{prompt_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == prompt_id

    def test_get_prompt_not_found(self, client: TestClient):
        """Test that getting a non-existent prompt returns 404.
        """
        response = client.get("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_update_prompt(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        updated_data = {
            "title": "Updated Title",
            "content": "Updated content for the prompt",
            "description": "Updated description",
            "collection_id": None,
        }
        time.sleep(0.1)

        response = client.put(f"/prompts/{prompt_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["updated_at"] != original_updated_at

    def test_update_prompt_not_found_returns_404(self, client: TestClient):
        response = client.put(
            "/prompts/nonexistent-id",
            json={"title": "T", "content": "C", "description": "D", "collection_id": None},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_update_prompt_invalid_collection_returns_400(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        response = client.put(
            f"/prompts/{prompt_id}",
            json={
                "title": "Updated",
                "content": "Updated content",
                "description": "Updated description",
                "collection_id": "missing-collection-id",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_patch_prompt(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        time.sleep(0.1)
        response = client.patch(f"/prompts/{prompt_id}", json={"title": "Patched Title"})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Patched Title"
        assert data["content"] == sample_prompt_data["content"]
        assert data["updated_at"] != original_updated_at

    def test_patch_prompt_no_fields_returns_400(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.patch(f"/prompts/{prompt_id}", json={})
        assert response.status_code == 400
        assert response.json()["detail"] == "No fields provided for update"

    def test_patch_prompt_not_found_returns_404(self, client: TestClient):
        response = client.patch("/prompts/nonexistent-id", json={"title": "Updated"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_patch_prompt_invalid_collection_returns_400(
        self, client: TestClient, sample_prompt_data
    ):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]
        response = client.patch(
            f"/prompts/{prompt_id}",
            json={"collection_id": "missing-collection-id"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_delete_prompt(self, client: TestClient, sample_prompt_data):
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        response = client.delete(f"/prompts/{prompt_id}")
        assert response.status_code == 204

        get_response = client.get(f"/prompts/{prompt_id}")
        assert get_response.status_code == 404

    def test_delete_prompt_not_found_returns_404(self, client: TestClient):
        response = client.delete("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    def test_list_prompts_sorted_newest_first(self, client: TestClient):
        client.post("/prompts", json={"title": "First", "content": "First prompt content"})
        time.sleep(0.1)
        client.post("/prompts", json={"title": "Second", "content": "Second prompt content"})

        response = client.get("/prompts")
        prompts = response.json()["prompts"]
        assert prompts[0]["title"] == "Second"
        assert prompts[1]["title"] == "First"

    def test_list_prompts_filter_by_collection_query_param(self, client: TestClient):
        col_a = client.post("/collections", json={"name": "A", "description": "desc"}).json()
        col_b = client.post("/collections", json={"name": "B", "description": "desc"}).json()

        client.post(
            "/prompts",
            json={"title": "A1", "content": "Prompt in A", "collection_id": col_a["id"]},
        )
        client.post(
            "/prompts",
            json={"title": "B1", "content": "Prompt in B", "collection_id": col_b["id"]},
        )

        response = client.get(f"/prompts?collection_id={col_a['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "A1"
        assert data["prompts"][0]["collection_id"] == col_a["id"]

    def test_list_prompts_search_query_param(self, client: TestClient):
        client.post(
            "/prompts",
            json={
                "title": "Code review checklist",
                "content": "Prompt body one",
                "description": "Looks for quality and bugs",
            },
        )
        client.post(
            "/prompts",
            json={
                "title": "Deployment runbook",
                "content": "Prompt body two",
                "description": "Release checklist",
            },
        )

        response = client.get("/prompts?search=review")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["title"] == "Code review checklist"

    def test_list_prompts_combined_filter_and_search(self, client: TestClient):
        collection = client.post(
            "/collections", json={"name": "Engineering", "description": "desc"}
        ).json()
        other = client.post("/collections", json={"name": "Other", "description": "desc"}).json()

        client.post(
            "/prompts",
            json={
                "title": "API review",
                "content": "Review backend",
                "description": "In engineering collection",
                "collection_id": collection["id"],
            },
        )
        client.post(
            "/prompts",
            json={
                "title": "API review",
                "content": "Review frontend",
                "description": "Different collection",
                "collection_id": other["id"],
            },
        )

        response = client.get(f"/prompts?collection_id={collection['id']}&search=api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["collection_id"] == collection["id"]


class TestCollections:
    """Tests for collection endpoints."""

    def test_create_collection(self, client: TestClient, sample_collection_data):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert "id" in data

    def test_create_collection_empty_name_returns_422(self, client: TestClient):
        response = client.post("/collections", json={"name": "", "description": "desc"})
        assert response.status_code == 422

    def test_list_collections(self, client: TestClient, sample_collection_data):
        client.post("/collections", json=sample_collection_data)
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert len(data["collections"]) == 1
        assert data["total"] == 1

    def test_get_collection_success(self, client: TestClient, sample_collection_data):
        create_response = client.post("/collections", json=sample_collection_data)
        collection_id = create_response.json()["id"]

        response = client.get(f"/collections/{collection_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == collection_id

    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Collection not found"

    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data):
        col_response = client.post("/collections", json=sample_collection_data)
        collection_id = col_response.json()["id"]

        prompt_response = client.post(
            "/prompts",
            json={
                "title": "Prompt in collection",
                "content": "Content for collection prompt",
                "collection_id": collection_id,
            },
        )
        prompt_id = prompt_response.json()["id"]

        delete_response = client.delete(f"/collections/{collection_id}")
        assert delete_response.status_code == 204

        prompt_after_delete = client.get(f"/prompts/{prompt_id}")
        assert prompt_after_delete.status_code == 200
        assert prompt_after_delete.json()["collection_id"] is None

    def test_delete_collection_not_found_returns_404(self, client: TestClient):
        response = client.delete("/collections/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Collection not found"

