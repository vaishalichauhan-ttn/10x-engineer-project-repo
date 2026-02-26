"""FastAPI routes for PromptLab"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
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
    PromptVersion,
    PromptVersionCreate,
    get_current_time,
)
from app.storage import storage
from app.utils import (
    filter_prompts_by_collection,
    search_prompts,
    sort_prompts_by_date,
)

app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_prompt_or_404(prompt_id: str) -> Prompt:
    prompt = storage.get_prompt(prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


def _get_collection_or_404(collection_id: str) -> Collection:
    collection = storage.get_collection(collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


def _get_prompt_version_or_404(
    prompt_id: str,
    version_number: int,
) -> PromptVersion:
    version = storage.get_prompt_version(prompt_id, version_number)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


def _ensure_collection_exists(collection_id: Optional[str]) -> None:
    if collection_id and storage.get_collection(collection_id) is None:
        raise HTTPException(status_code=400, detail="Collection not found")


def _build_prompt_snapshot(
    existing_prompt: Prompt,
    *,
    title: str,
    content: str,
    description: Optional[str],
    collection_id: Optional[str],
) -> Prompt:
    return Prompt(
        id=existing_prompt.id,
        title=title,
        content=content,
        description=description,
        collection_id=collection_id,
        created_at=existing_prompt.created_at,
        updated_at=get_current_time(),
    )


def _store_prompt_update(
    prompt_id: str,
    updated_prompt: Prompt,
    *,
    version_note: Optional[str] = None,
) -> Prompt:
    updated = storage.update_prompt(prompt_id, updated_prompt)
    if updated is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    storage.create_prompt_version(updated, note=version_note)
    return updated


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Checks the health status of the application.
    Args:
        None
    Returns:
        HealthResponse: A response object containing the application's
            health status and version.
    Raises:
        None
    """
    return HealthResponse(status="healthy", version=__version__)


@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None,
) -> PromptList:
    """Retrieve prompts, optionally filtered by collection and search query.

    Args:
        collection_id (Optional[str]): The ID of the collection to filter
            prompts by.
        search (Optional[str]): A search query to filter prompts.

    Returns:
        PromptList: Prompts matching the specified filters and sorted by
            date.

    Raises:
        ValueError: If there is an issue with the data retrieval or processing.
    """
    prompt_list = storage.get_all_prompts()
    if collection_id:
        prompt_list = filter_prompts_by_collection(prompt_list, collection_id)
    if search:
        prompt_list = search_prompts(prompt_list, search)
    sorted_prompts = sort_prompts_by_date(prompt_list, descending=True)
    return PromptList(prompts=sorted_prompts, total=len(sorted_prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str) -> Prompt:
    """Retrieve a prompt by its ID.

    Args:
        prompt_id (str): The unique identifier for the prompt.

    Returns:
        Prompt: The prompt data if found.

    Raises:
        HTTPException: If the prompt is not found, an HTTP 404 error is raised.
    """
    return _get_prompt_or_404(prompt_id)


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate) -> Prompt:
    """Create a new prompt and store it in the database.

    Args:
        prompt_data (PromptCreate): The data required to create a new prompt,
            including the prompt text and optionally a collection ID.

    Returns:
        Prompt: The newly created prompt stored in the database.

    Raises:
        HTTPException: If the provided collection_id does not exist in
            the database, a 400 error is raised with the message
            "Collection not found".
    """
    _ensure_collection_exists(prompt_data.collection_id)
    return storage.create_prompt(Prompt(**prompt_data.model_dump()))


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate) -> Prompt:
    """Update an existing prompt with new data.

    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        prompt_data (PromptUpdate): An object containing the updated data
            for the prompt.

    Returns:
        Prompt: The updated prompt object.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the provided collection is not found, a 400
            error is raised.
    """
    existing_prompt = _get_prompt_or_404(prompt_id)
    _ensure_collection_exists(prompt_data.collection_id)
    updated_prompt = _build_prompt_snapshot(
        existing_prompt,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
    )
    return _store_prompt_update(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPatch) -> Prompt:
    """
    Partially updates an existing prompt with new data fields.

    Args:
        prompt_id (str): The identifier of the prompt to update.
        prompt_data (PromptPatch): The data fields to update on the
            prompt, which could include title, content, description, or
            collection_id.

    Returns:
        Prompt: The updated prompt object after applying changes.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the provided collection is not found, a 400
            error is raised.
    """
    existing_prompt = _get_prompt_or_404(prompt_id)
    update_fields = prompt_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )
    _ensure_collection_exists(update_fields.get("collection_id"))
    updated_prompt = _build_prompt_snapshot(
        existing_prompt,
        title=update_fields.get("title", existing_prompt.title),
        content=update_fields.get("content", existing_prompt.content),
        description=update_fields.get(
            "description",
            existing_prompt.description,
        ),
        collection_id=update_fields.get(
            "collection_id",
            existing_prompt.collection_id,
        ),
    )
    return _store_prompt_update(prompt_id, updated_prompt)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str) -> None:
    """Deletes a prompt by its ID.

    Args:
        prompt_id (str): The unique identifier of the prompt to be deleted.

    Returns:
        None

    Raises:
        HTTPException: If the prompt with the given ID is not found,
            raises a 404 error.
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


@app.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersion])
def list_prompt_versions(
    prompt_id: str,
    limit: Optional[int] = None,
    offset: int = 0,
) -> list[PromptVersion]:
    """List all versions for a prompt in newest-first order.

    Args:
        prompt_id (str): The unique identifier of the prompt whose
            versions are requested.
        limit (Optional[int]): Maximum number of versions to return.
        offset (int): Number of newest versions to skip before returning
            results.

    Returns:
        list[PromptVersion]: A paginated list of prompt version snapshots.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
    """
    _get_prompt_or_404(prompt_id)
    return storage.get_prompt_versions(prompt_id, limit=limit, offset=offset)


@app.get(
    "/prompts/{prompt_id}/versions/{version_number}",
    response_model=PromptVersion,
)
def get_prompt_version(prompt_id: str, version_number: int) -> PromptVersion:
    """Retrieve a specific version snapshot for a prompt.

    Args:
        prompt_id (str): The unique identifier of the prompt.
        version_number (int): The version number to retrieve.

    Returns:
        PromptVersion: The requested prompt version snapshot.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the version is not found, a 404 error is raised.
    """
    _get_prompt_or_404(prompt_id)
    return _get_prompt_version_or_404(prompt_id, version_number)


@app.post(
    "/prompts/{prompt_id}/versions",
    response_model=PromptVersion,
    status_code=201,
)
def create_manual_prompt_version(
    prompt_id: str,
    checkpoint_data: Optional[PromptVersionCreate] = None,
) -> PromptVersion:
    """Create a manual version checkpoint from the current prompt state.

    Args:
        prompt_id (str): The unique identifier of the prompt to checkpoint.
        checkpoint_data (Optional[PromptVersionCreate]): Optional
            checkpoint payload that can include a note for the snapshot.

    Returns:
        PromptVersion: The newly created version snapshot.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
    """
    prompt = _get_prompt_or_404(prompt_id)
    note = checkpoint_data.note if checkpoint_data else None
    return storage.create_prompt_version(prompt, note=note)


@app.post(
    "/prompts/{prompt_id}/versions/{version_number}/revert",
    response_model=Prompt,
)
def revert_prompt_to_version(prompt_id: str, version_number: int) -> Prompt:
    """Revert a prompt to the data stored in a previous version.

    Args:
        prompt_id (str): The unique identifier of the prompt to revert.
        version_number (int): The target version number to restore.

    Returns:
        Prompt: The updated prompt after the revert operation.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the target version is not found, a 404 error
            is raised.
        HTTPException: If the prompt already matches the target version,
            a 409 error is raised.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    version = storage.get_prompt_version(prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    is_noop = (
        existing.title == version.title
        and existing.content == version.content
        and existing.description == version.description
        and existing.collection_id == version.collection_id
    )
    if is_noop:
        raise HTTPException(
            status_code=409,
            detail="Prompt already matches target version",
        )

    reverted_prompt = Prompt(
        id=existing.id,
        title=version.title,
        content=version.content,
        description=version.description,
        collection_id=version.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time(),
    )
    updated = storage.update_prompt(prompt_id, reverted_prompt)
    storage.create_prompt_version(
        updated,
        note=f"Reverted to version {version_number}",
    )
    return updated


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections() -> CollectionList:
    """Retrieve a list of all collections.

    Returns:
        CollectionList: An object containing a list of all collections and
                        the total number of collections.
    """
    collection_list = storage.get_all_collections()
    return CollectionList(
        collections=collection_list,
        total=len(collection_list),
    )


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str) -> Collection:
    """Retrieve a specific collection by its ID.

    Args:
        collection_id (str): The unique identifier of the collection to
            retrieve.

    Returns:
        Collection: The collection object if found.

    Raises:
        HTTPException: If the collection with the given ID is not found,
                       raises a 404 HTTPException.
    """
    return _get_collection_or_404(collection_id)


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate) -> Collection:
    """Create a new collection.

    Args:
        collection_data (CollectionCreate): The data required to create
            a new collection.

    Returns:
        Collection: The newly created collection object.
    """
    return storage.create_collection(
        Collection(**collection_data.model_dump())
    )


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str) -> None:
    """Delete a collection and disassociate it from its prompts.

    This function deletes a collection specified by the provided
    collection_id. If the collection is found, it will be removed and
    all associated prompts will have their collection_id set to None.

    Args:
        collection_id (str): The unique identifier of the collection to
            be deleted.

    Returns:
        None

    Raises:
        HTTPException: If the collection with the specified
            collection_id is not found, a 404 error is raised.
    """
    # Ensure the collection exists and can be deleted
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")

    # Retrieve all prompts with this collection_id
    prompts = storage.get_prompts_by_collection(collection_id)

    # Set collection_id to None for each retrieved prompt
    for prompt in prompts:
        prompt.collection_id = None
        storage.update_prompt(prompt.id, prompt)

    return None