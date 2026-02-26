"""Utility functions for PromptLab"""

import re
from typing import Optional

from app.models import Prompt

TEMPLATE_VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def sort_prompts_by_date(
    prompts: list[Prompt],
    descending: bool = True,
) -> list[Prompt]:
    """Sort prompts by creation date.

    Args:
        prompts (List[Prompt]): A list of Prompt objects to be sorted.
        descending (bool): Determines sort order. If True, sorts from
            newest to oldest; if False, sorts from oldest to newest.
            Default is True.

    Returns:
        List[Prompt]: A sorted list of Prompt objects by creation date.

    Example:
        >>> sorted_prompts = sort_prompts_by_date(prompts, descending=False)
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(
    prompts: list[Prompt],
    collection_id: Optional[str],
) -> list[Prompt]:
    """Filter prompts by collection ID.

    Args:
        prompts (List[Prompt]): A list of Prompt objects to be filtered.
        collection_id (str): The collection ID to filter prompts by.

    Returns:
        List[Prompt]: Prompt objects that belong to the specified
            collection.

    Example:
        >>> filtered_prompts = filter_prompts_by_collection(
        ...     prompts, "collection_123"
        ... )
    """
    return [p for p in prompts if p.collection_id == collection_id]


def search_prompts(prompts: list[Prompt], query: str) -> list[Prompt]:
    """Search prompts by title or description matching the query.

    Args:
        prompts (List[Prompt]): A list of Prompt objects to be searched.
        query (str): The search string to match against prompt titles
            and descriptions.

    Returns:
        List[Prompt]: Prompt objects that match the search criteria.

    Example:
        >>> searched_prompts = search_prompts(prompts, "AI")
    """
    query_lower = query.lower()
    return [
        p for p in prompts
        if (
            query_lower in p.title.lower()
            or (
                p.description
                and query_lower in p.description.lower()
            )
        )
    ]


def validate_prompt_content(content: Optional[str]) -> bool:
    """Check if prompt content is valid.

    Args:
        content (str): The content of the prompt to validate.

    Returns:
        bool: True if the content is valid, False otherwise.

    Example:
        valid = validate_prompt_content("This is a valid prompt")
        # valid will be True

        invalid = validate_prompt_content("   ")
        # invalid will be False
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> list[str]:
    """Extract template variables from prompt content.

    Variables are in the format {{variable_name}}.

    Args:
        content (str): The string containing template variables to be
            extracted.

    Returns:
        List[str]: A list of extracted variable names.

    Example:
        >>> extract_variables("Hello, {{user}}! Today is {{day}}.")
        ['user', 'day']
    """
    return TEMPLATE_VARIABLE_PATTERN.findall(content)
