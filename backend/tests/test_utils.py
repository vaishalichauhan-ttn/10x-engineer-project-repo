"""Unit tests for utility functions."""

from datetime import datetime, timedelta

import pytest

from app.models import Prompt
from app.utils import (
    extract_variables,
    filter_prompts_by_collection,
    search_prompts,
    sort_prompts_by_date,
    validate_prompt_content,
)


def _prompt(
    prompt_id: str,
    title: str,
    content: str,
    *,
    created_at: datetime,
    description: str | None = None,
    collection_id: str | None = None,
) -> Prompt:
    """Helper for explicit prompt construction in tests."""
    return Prompt(
        id=prompt_id,
        title=title,
        content=content,
        description=description,
        collection_id=collection_id,
        created_at=created_at,
        updated_at=created_at,
    )


class TestSortPromptsByDate:
    """Tests for sort_prompts_by_date."""

    def test_sorts_descending_by_default(self):
        base = datetime.utcnow()
        older = _prompt("1", "Older", "Valid content 1", created_at=base)
        newer = _prompt("2", "Newer", "Valid content 2", created_at=base + timedelta(seconds=30))

        result = sort_prompts_by_date([older, newer])

        assert [prompt.id for prompt in result] == ["2", "1"]

    def test_sorts_ascending_when_descending_is_false(self):
        base = datetime.utcnow()
        older = _prompt("1", "Older", "Valid content 1", created_at=base)
        newer = _prompt("2", "Newer", "Valid content 2", created_at=base + timedelta(seconds=30))

        result = sort_prompts_by_date([newer, older], descending=False)

        assert [prompt.id for prompt in result] == ["1", "2"]

    def test_returns_empty_list_when_input_is_empty(self):
        assert sort_prompts_by_date([]) == []

    def test_raises_type_error_for_none_input(self):
        with pytest.raises(TypeError):
            sort_prompts_by_date(None)  # type: ignore[arg-type]


class TestFilterPromptsByCollection:
    """Tests for filter_prompts_by_collection."""

    def test_returns_only_prompts_with_matching_collection_id(self):
        now = datetime.utcnow()
        p1 = _prompt("1", "One", "Valid content 1", created_at=now, collection_id="c1")
        p2 = _prompt("2", "Two", "Valid content 2", created_at=now, collection_id="c2")
        p3 = _prompt("3", "Three", "Valid content 3", created_at=now, collection_id="c1")

        result = filter_prompts_by_collection([p1, p2, p3], "c1")

        assert [prompt.id for prompt in result] == ["1", "3"]

    def test_returns_empty_list_when_no_prompt_matches(self):
        now = datetime.utcnow()
        prompt = _prompt("1", "One", "Valid content 1", created_at=now, collection_id="c1")

        result = filter_prompts_by_collection([prompt], "missing")

        assert result == []

    def test_returns_prompts_with_none_collection_when_collection_id_is_none(self):
        now = datetime.utcnow()
        p1 = _prompt("1", "One", "Valid content 1", created_at=now, collection_id=None)
        p2 = _prompt("2", "Two", "Valid content 2", created_at=now, collection_id="c1")

        result = filter_prompts_by_collection([p1, p2], None)  # type: ignore[arg-type]

        assert [prompt.id for prompt in result] == ["1"]


class TestSearchPrompts:
    """Tests for search_prompts."""

    def test_matches_title_and_description_case_insensitively(self):
        now = datetime.utcnow()
        title_match = _prompt(
            "1",
            "Code Review Checklist",
            "Valid content 1",
            created_at=now,
            description="General checklist",
        )
        description_match = _prompt(
            "2",
            "Deployment Guide",
            "Valid content 2",
            created_at=now,
            description="Review release steps",
        )
        no_match = _prompt(
            "3",
            "Standup Notes",
            "Valid content 3",
            created_at=now,
            description="Team updates",
        )

        result = search_prompts([title_match, description_match, no_match], "ReViEw")

        assert [prompt.id for prompt in result] == ["1", "2"]

    def test_returns_empty_list_when_no_matches(self):
        now = datetime.utcnow()
        prompt = _prompt("1", "Alpha", "Valid content 1", created_at=now, description="Bravo")

        result = search_prompts([prompt], "charlie")

        assert result == []

    def test_returns_all_prompts_when_query_is_empty_string(self):
        now = datetime.utcnow()
        p1 = _prompt("1", "Alpha", "Valid content 1", created_at=now)
        p2 = _prompt("2", "Beta", "Valid content 2", created_at=now, description="desc")

        result = search_prompts([p1, p2], "")

        assert [prompt.id for prompt in result] == ["1", "2"]

    def test_raises_attribute_error_for_none_query(self):
        now = datetime.utcnow()
        prompt = _prompt("1", "Alpha", "Valid content 1", created_at=now)

        with pytest.raises(AttributeError):
            search_prompts([prompt], None)  # type: ignore[arg-type]


class TestValidatePromptContent:
    """Tests for validate_prompt_content."""

    def test_returns_true_for_valid_content(self):
        assert validate_prompt_content("This content is valid.") is True

    def test_returns_false_for_blank_or_short_content(self):
        assert validate_prompt_content("") is False
        assert validate_prompt_content("    ") is False
        assert validate_prompt_content("short") is False

    def test_trims_whitespace_before_length_validation(self):
        assert validate_prompt_content("     1234567890      ") is True
        assert validate_prompt_content("     123456789       ") is False

    def test_returns_false_for_none_content(self):
        assert validate_prompt_content(None) is False  # type: ignore[arg-type]


class TestExtractVariables:
    """Tests for extract_variables."""

    def test_extracts_all_variables_in_order(self):
        content = "Hello {{user}}, run {{task}} in {{environment}}."
        assert extract_variables(content) == ["user", "task", "environment"]

    def test_returns_duplicates_when_variable_repeats(self):
        content = "{{name}} and again {{name}}"
        assert extract_variables(content) == ["name", "name"]

    def test_ignores_invalid_or_spaced_patterns(self):
        content = "{{valid_1}} {{not valid}} {{two-words}} {{{nested}}} {{}}"
        assert extract_variables(content) == ["valid_1", "nested"]

    def test_returns_empty_list_for_no_variables(self):
        assert extract_variables("No template placeholders here.") == []

    def test_raises_type_error_for_none_content(self):
        with pytest.raises(TypeError):
            extract_variables(None)  # type: ignore[arg-type]
