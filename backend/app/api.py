"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate, PromptPatch,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    PromptVersion, PromptVersionCreate, get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Checks the health status of the application.
    Args:
        None
    Returns:
        HealthResponse: A response object containing the application's health status and version.
    Raises:
        None
    """
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None
):
    """Retrieve a list of prompts, optionally filtered by collection and search query.

    Args:
        collection_id (Optional[str]): The ID of the collection to filter prompts by.
        search (Optional[str]): A search query to filter prompts.

    Returns:
        PromptList: A list of prompts matching the specified filters and sorted by date.

    Raises:
        ValueError: If there is an issue with the data retrieval or processing.
    """
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)
    
    # Sort by date (newest first)
    # Note: There might be an issue with the sorting...
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a prompt by its ID.

    Args:
        prompt_id (str): The unique identifier for the prompt.

    Returns:
        Prompt: The prompt data if found.

    Raises:
        HTTPException: If the prompt is not found, an HTTP 404 error is raised.
    """
    prompt = storage.get_prompt(prompt_id)
    
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt and store it in the database.

    Args:
        prompt_data (PromptCreate): The data required to create a new prompt,
            including the prompt text and optionally a collection ID.

    Returns:
        Prompt: The newly created prompt stored in the database.

    Raises:
        HTTPException: If the provided collection_id does not exist in the database, a 400 error is raised with the message "Collection not found".
    """
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Update an existing prompt with new data.

    Args:
        prompt_id (str): The unique identifier of the prompt to update.
        prompt_data (PromptUpdate): An object containing the updated data for the prompt.

    Returns:
        Prompt: The updated prompt object.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the provided collection is not found, a 400 error is raised.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()
    )
    
    updated = storage.update_prompt(prompt_id, updated_prompt)
    storage.create_prompt_version(updated)
    return updated

@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPatch):
    """
    Partially updates an existing prompt with new data fields.

    Args:
        prompt_id (str): The identifier of the prompt to update.
        prompt_data (PromptPatch): The data fields to update on the prompt which
                                   could include title, content, description, or collection_id.

    Returns:
        Prompt: The updated prompt object after applying changes.

    Raises:
        HTTPException: If the prompt is not found, a 404 error is raised.
        HTTPException: If the provided collection is not found, a 400 error is raised.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Extract only provided fields
    update_data = prompt_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # Validate collection if being updated
    if "collection_id" in update_data and update_data["collection_id"]:
        collection = storage.get_collection(update_data["collection_id"])
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    # Merge existing data with updates
    updated_prompt = Prompt(
        id=existing.id,
        title=update_data.get("title", existing.title),
        content=update_data.get("content", existing.content),
        description=update_data.get("description", existing.description),
        collection_id=update_data.get("collection_id", existing.collection_id),
        created_at=existing.created_at,
        updated_at=get_current_time(),
    )

    updated = storage.update_prompt(prompt_id, updated_prompt)
    storage.create_prompt_version(updated)
    return updated

@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Deletes a prompt by its ID.

    Args:
        prompt_id (str): The unique identifier of the prompt to be deleted.

    Returns:
        None

    Raises:
        HTTPException: If the prompt with the given ID is not found, raises a 404 error.
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


@app.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersion])
def list_prompt_versions(
    prompt_id: str,
    limit: Optional[int] = None,
    offset: int = 0,
):
    """List versions for a prompt, newest-first."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return storage.get_prompt_versions(prompt_id, limit=limit, offset=offset)


@app.get("/prompts/{prompt_id}/versions/{version_number}", response_model=PromptVersion)
def get_prompt_version(prompt_id: str, version_number: int):
    """Get a single version snapshot."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    version = storage.get_prompt_version(prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    return version


@app.post("/prompts/{prompt_id}/versions", response_model=PromptVersion, status_code=201)
def create_manual_prompt_version(
    prompt_id: str, checkpoint_data: Optional[PromptVersionCreate] = None
):
    """Create a manual version checkpoint for the current prompt state."""
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    note = checkpoint_data.note if checkpoint_data else None
    return storage.create_prompt_version(prompt, note=note)


@app.post("/prompts/{prompt_id}/versions/{version_number}/revert", response_model=Prompt)
def revert_prompt_to_version(prompt_id: str, version_number: int):
    """Revert a prompt to a historical version snapshot."""
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
        raise HTTPException(status_code=409, detail="Prompt already matches target version")

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
    storage.create_prompt_version(updated, note=f"Reverted to version {version_number}")
    return updated


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    """Retrieve a list of all collections.

    Returns:
        CollectionList: An object containing a list of all collections and
                        the total number of collections.
    """
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a specific collection by its ID.

    Args:
        collection_id (str): The unique identifier of the collection to retrieve.

    Returns:
        Collection: The collection object if found.

    Raises:
        HTTPException: If the collection with the given ID is not found,
                       raises a 404 HTTPException.
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new collection.

    Args:
        collection_data (CollectionCreate): The data required to create a new collection.

    Returns:
        Collection: The newly created collection object.
    """
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection and disassociate it from its prompts.

    This function deletes a collection specified by the provided 
    collection_id. If the collection is found, it will be removed and 
    all associated prompts will have their collection_id set to None.

    Args:
        collection_id (str): The unique identifier of the collection to be deleted.

    Returns:
        None

    Raises:
        HTTPException: If the collection with the specified collection_id 
                       is not found, a 404 error is raised.
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

