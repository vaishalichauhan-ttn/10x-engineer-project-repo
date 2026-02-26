"""Unit tests for in-memory storage behavior."""

import pytest

from app.models import Collection, Prompt
from app.storage import Storage


class TestPromptCRUD:
    """Prompt CRUD operations on Storage."""

    def test_prompt_crud_operations(self):
        storage = Storage()
        prompt = Prompt(id="prompt-1", title="Initial", content="Initial content")

        created = storage.create_prompt(prompt)
        assert created.id == "prompt-1"

        fetched = storage.get_prompt("prompt-1")
        assert fetched is not None
        assert fetched.title == "Initial"

        updated_prompt = Prompt(id="prompt-1", title="Updated", content="Updated content")
        updated = storage.update_prompt("prompt-1", updated_prompt)
        assert updated is not None
        assert updated.title == "Updated"
        assert storage.get_prompt("prompt-1").content == "Updated content"

        deleted = storage.delete_prompt("prompt-1")
        assert deleted is True
        assert storage.get_prompt("prompt-1") is None

    def test_collection_crud_operations(self):
        storage = Storage()
        collection = Collection(id="collection-1", name="Engineering", description="Team prompts")

        created = storage.create_collection(collection)
        assert created.id == "collection-1"

        fetched = storage.get_collection("collection-1")
        assert fetched is not None
        assert fetched.name == "Engineering"

        deleted = storage.delete_collection("collection-1")
        assert deleted is True
        assert storage.get_collection("collection-1") is None


class TestInSessionPersistence:
    """Data should persist for the lifetime of a Storage instance."""

    def test_data_persists_within_same_storage_instance(self):
        storage = Storage()
        collection = Collection(id="collection-1", name="Saved")
        prompt = Prompt(
            id="prompt-1",
            title="Persisted prompt",
            content="Still there",
            collection_id="collection-1",
        )

        storage.create_collection(collection)
        storage.create_prompt(prompt)

        assert len(storage.get_all_collections()) == 1
        assert len(storage.get_all_prompts()) == 1
        assert storage.get_prompt("prompt-1").collection_id == "collection-1"

        # Multiple reads in the same session should return the stored entries.
        assert storage.get_prompt("prompt-1") is not None
        assert storage.get_collection("collection-1") is not None

    def test_data_is_isolated_between_storage_instances(self):
        first = Storage()
        second = Storage()
        first.create_prompt(Prompt(id="prompt-1", title="Only first", content="A"))

        assert first.get_prompt("prompt-1") is not None
        assert second.get_prompt("prompt-1") is None


class TestStorageEdgeCases:
    """Edge and non-happy-path cases."""

    def test_create_prompt_with_duplicate_id_raises_key_error(self):
        storage = Storage()
        storage.create_prompt(Prompt(id="duplicate", title="One", content="A"))

        with pytest.raises(KeyError):
            storage.create_prompt(Prompt(id="duplicate", title="Two", content="B"))

    def test_update_delete_and_get_missing_entities(self):
        storage = Storage()

        assert storage.get_prompt("missing-prompt") is None
        assert storage.get_collection("missing-collection") is None
        assert storage.update_prompt(
            "missing-prompt",
            Prompt(id="missing-prompt", title="T", content="C"),
        ) is None
        assert storage.delete_prompt("missing-prompt") is False
        assert storage.delete_collection("missing-collection") is False

    def test_get_prompts_by_collection_returns_only_matching_prompts(self):
        storage = Storage()
        storage.create_prompt(Prompt(id="p1", title="A", content="X", collection_id="c1"))
        storage.create_prompt(Prompt(id="p2", title="B", content="Y", collection_id="c2"))
        storage.create_prompt(Prompt(id="p3", title="C", content="Z", collection_id="c1"))

        prompts = storage.get_prompts_by_collection("c1")

        assert len(prompts) == 2
        assert {prompt.id for prompt in prompts} == {"p1", "p3"}

    def test_clear_removes_all_prompts_and_collections(self):
        storage = Storage()
        storage.create_collection(Collection(id="c1", name="Collection"))
        storage.create_prompt(Prompt(id="p1", title="A", content="B"))

        storage.clear()

        assert storage.get_all_prompts() == []
        assert storage.get_all_collections() == []


class TestPromptVersionStorage:
    """Version lifecycle operations on Storage."""

    def test_create_and_fetch_versions(self):
        storage = Storage()
        prompt = Prompt(id="p1", title="Initial", content="Initial content")
        storage.create_prompt(prompt)

        prompt_v1 = Prompt(id="p1", title="V1", content="Content 1")
        storage.update_prompt("p1", prompt_v1)
        version1 = storage.create_prompt_version(prompt_v1)

        prompt_v2 = Prompt(id="p1", title="V2", content="Content 2")
        storage.update_prompt("p1", prompt_v2)
        version2 = storage.create_prompt_version(prompt_v2, note="manual checkpoint")

        assert version1.version_number == 1
        assert version2.version_number == 2
        assert version2.note == "manual checkpoint"

        versions = storage.get_prompt_versions("p1")
        assert [v.version_number for v in versions] == [2, 1]
        assert versions[0].title == "V2"

        specific = storage.get_prompt_version("p1", 1)
        assert specific is not None
        assert specific.title == "V1"

    def test_get_prompt_versions_respects_limit_and_offset(self):
        storage = Storage()
        prompt = Prompt(id="p1", title="Initial", content="Initial content")
        storage.create_prompt(prompt)

        for index in range(1, 4):
            updated = Prompt(id="p1", title=f"V{index}", content=f"Content {index}")
            storage.update_prompt("p1", updated)
            storage.create_prompt_version(updated)

        versions = storage.get_prompt_versions("p1", limit=1, offset=1)
        assert len(versions) == 1
        assert versions[0].version_number == 2

    def test_delete_prompt_also_deletes_versions(self):
        storage = Storage()
        prompt = Prompt(id="p1", title="Initial", content="Initial content")
        storage.create_prompt(prompt)
        storage.create_prompt_version(prompt)

        assert storage.delete_prompt("p1") is True
        assert storage.get_prompt_versions("p1") == []
        assert storage.get_prompt_version("p1", 1) is None

    def test_clear_removes_versions(self):
        storage = Storage()
        prompt = Prompt(id="p1", title="Initial", content="Initial content")
        storage.create_prompt(prompt)
        storage.create_prompt_version(prompt)

        storage.clear()

        assert storage.get_prompt_versions("p1") == []
