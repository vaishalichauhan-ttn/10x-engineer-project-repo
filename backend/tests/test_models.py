"""Unit tests for Pydantic models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    Collection,
    CollectionCreate,
    CollectionList,
    HealthResponse,
    Prompt,
    PromptCreate,
    PromptList,
    PromptPatch,
    PromptUpdate,
)


class TestModelValidation:
    """Validation constraints for request/response models."""

    def test_prompt_create_validates_required_and_length_constraints(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="", content="valid content")

        with pytest.raises(ValidationError):
            PromptCreate(title="Valid", content="")

        with pytest.raises(ValidationError):
            PromptCreate(title="x" * 201, content="valid content")

        with pytest.raises(ValidationError):
            PromptCreate(
                title="Valid",
                content="valid content",
                description="d" * 501,
            )

    def test_prompt_update_uses_same_validation_rules(self):
        with pytest.raises(ValidationError):
            PromptUpdate(title="", content="updated content")

        with pytest.raises(ValidationError):
            PromptUpdate(title="Updated", content="")

    def test_prompt_patch_allows_partial_fields_but_validates_if_present(self):
        # Partial update with no fields is allowed by model shape.
        patch = PromptPatch()
        assert patch.title is None
        assert patch.content is None

        with pytest.raises(ValidationError):
            PromptPatch(title="")

        with pytest.raises(ValidationError):
            PromptPatch(content="")

        with pytest.raises(ValidationError):
            PromptPatch(description="d" * 501)

    def test_collection_create_validates_name_and_description_limits(self):
        with pytest.raises(ValidationError):
            CollectionCreate(name="")

        with pytest.raises(ValidationError):
            CollectionCreate(name="x" * 101)

        with pytest.raises(ValidationError):
            CollectionCreate(name="Engineering", description="d" * 501)


class TestDefaultValues:
    """Default values produced by model factories."""

    def test_prompt_generates_id_and_timestamps(self):
        prompt = Prompt(title="Prompt title", content="Prompt content")

        assert isinstance(prompt.id, str)
        assert prompt.id
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)
        assert prompt.description is None
        assert prompt.collection_id is None

    def test_collection_generates_id_and_created_at(self):
        collection = Collection(name="My collection")

        assert isinstance(collection.id, str)
        assert collection.id
        assert isinstance(collection.created_at, datetime)
        assert collection.description is None


class TestSerialization:
    """Serialization behavior for individual and nested models."""

    def test_prompt_serialization_to_dict_and_json_mode(self):
        prompt = Prompt(
            id="prompt-1",
            title="Serialize me",
            content="Content",
            description="Description",
            collection_id="collection-1",
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 1, 1, 0, 0),
        )

        data = prompt.model_dump()
        assert data["id"] == "prompt-1"
        assert data["title"] == "Serialize me"
        assert data["created_at"] == datetime(2024, 1, 1, 0, 0, 0)

        json_ready = prompt.model_dump(mode="json")
        assert json_ready["created_at"] == "2024-01-01T00:00:00"
        assert json_ready["updated_at"] == "2024-01-01T01:00:00"

    def test_collection_and_response_models_serialize_nested_payloads(self):
        collection = Collection(
            id="collection-1",
            name="Engineering",
            description="Collection description",
            created_at=datetime(2024, 1, 2, 0, 0, 0),
        )
        prompt = Prompt(
            id="prompt-1",
            title="T",
            content="C",
            collection_id=collection.id,
            created_at=datetime(2024, 1, 2, 0, 0, 0),
            updated_at=datetime(2024, 1, 2, 0, 30, 0),
        )

        prompt_list = PromptList(prompts=[prompt], total=1)
        collection_list = CollectionList(collections=[collection], total=1)
        health = HealthResponse(status="healthy", version="1.0.0")

        prompt_payload = prompt_list.model_dump(mode="json")
        collection_payload = collection_list.model_dump(mode="json")
        health_payload = health.model_dump()

        assert prompt_payload["total"] == 1
        assert prompt_payload["prompts"][0]["id"] == "prompt-1"
        assert prompt_payload["prompts"][0]["created_at"] == "2024-01-02T00:00:00"

        assert collection_payload["total"] == 1
        assert collection_payload["collections"][0]["id"] == "collection-1"
        assert collection_payload["collections"][0]["created_at"] == "2024-01-02T00:00:00"

        assert health_payload == {"status": "healthy", "version": "1.0.0"}
