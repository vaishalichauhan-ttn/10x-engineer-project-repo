"""In-memory storage for PromptLab

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.
"""

from typing import Optional

from app.models import Collection, Prompt, PromptVersion


class Storage:
    """Manage storage operations for prompts and collections.

    This class provides methods to create, retrieve, update, and delete
    prompts and collections. It also allows fetching all prompts or
    collections, and retrieving prompts by their associated collection.
    """
    def __init__(self) -> None:
        self._prompts: dict[str, Prompt] = {}
        self._collections: dict[str, Collection] = {}
        self._prompt_versions: dict[str, list[PromptVersion]] = {}
    
    # ============== Prompt Operations ==============
    
    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Adds a new prompt to the storage.

        Args:
            prompt (Prompt): The prompt to be added. It must include a unique `id`.
        Returns:
            Prompt: The same `Prompt` object that was added to the storage.

        Raises:
            KeyError: If a prompt with the same `id` already exists.

        Example usage:
            prompt = Prompt(id='1', text='Example prompt')
            storage.create_prompt(prompt)
        """
        if prompt.id in self._prompts:
            raise KeyError(f"A prompt with id '{prompt.id}' already exists.")

        self._prompts[prompt.id] = prompt
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieves a prompt by its ID.

        Args:
            prompt_id (str): The unique identifier of the prompt to retrieve.

        Returns:
            Optional[Prompt]: The prompt object if found, otherwise None.

        Raises:
            KeyError: If the prompt_id does not exist in the storage.

        Example usage:
            prompt = storage_instance.get_prompt("prompt123")
            if prompt:
                print(prompt.content)
        """
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> list[Prompt]:
        """Retrieves all stored prompts.

        This method returns a list of all prompt objects currently stored in the system.

        Returns:
            List[Prompt]: A list containing all the prompt objects.

        Raises:
            None

        Example:
            prompts = storage_instance.get_all_prompts()
        """
        return list(self._prompts.values())
    
    def update_prompt(
        self,
        prompt_id: str,
        prompt: Prompt,
    ) -> Optional[Prompt]:
        """Update an existing prompt with new data.

        Args:
            prompt_id (str): The unique identifier for the prompt to update.
            prompt (Prompt): The Prompt object containing updated data.

        Returns:
            Optional[Prompt]: The updated Prompt object if successful;
                None if the prompt_id does not exist.

        Raises:
           None

        Example usage:
            updated_prompt = storage.update_prompt(
                prompt_id="123",
                prompt=new_prompt,
            )
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Deletes a prompt from storage.

        Args:
            prompt_id (str): The unique identifier of the prompt to be deleted.

        Returns:
            bool: True if the prompt was successfully deleted, False if the prompt was not found.

        Raises:
            KeyError: If the prompt_id is invalid or not present in the storage.

        Example:
            storage = Storage()
            storage.delete_prompt('example_id')
        """

        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            self._prompt_versions.pop(prompt_id, None)
            return True
        return False

    # ============== Prompt Version Operations ==============

    def create_prompt_version(
        self,
        prompt: Prompt,
        note: Optional[str] = None,
    ) -> PromptVersion:
        """Create and store a new immutable version snapshot for a prompt."""
        versions = self._prompt_versions.get(prompt.id, [])
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=len(versions) + 1,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            collection_id=prompt.collection_id,
            note=note,
        )
        versions.append(version)
        self._prompt_versions[prompt.id] = versions
        return version

    def get_prompt_versions(
        self,
        prompt_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[PromptVersion]:
        """Get prompt versions sorted newest-first with optional pagination."""
        versions = list(reversed(self._prompt_versions.get(prompt_id, [])))
        if offset < 0:
            offset = 0
        if limit is None:
            return versions[offset:]
        return versions[offset : offset + limit]

    def get_prompt_version(
        self,
        prompt_id: str,
        version_number: int,
    ) -> Optional[PromptVersion]:
        """Get a specific version by prompt id and version number."""
        prompt_versions = self._prompt_versions.get(prompt_id, [])
        for version in prompt_versions:
            if version.version_number == version_number:
                return version
        return None

    # ============== Collection Operations ==============

    def create_collection(self, collection: Collection) -> Collection:
        """Adds a new collection to the storage.

        Args:
            collection (Collection): The collection object to be added.

        Returns:
            Collection: The added collection object.

        Raises:
            ValueError: If a collection with the same ID already exists.

        Example:
            collection = Collection(id="123", name="Sample Collection")
            storage.create_collection(collection)
        """
        self._collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its ID.

        Args:
            collection_id (str): The unique identifier for the collection to retrieve.

        Returns:
            Optional[Collection]: The collection associated with the
                given ID, if it exists, otherwise None.

        Raises:
            KeyError: If the collection_id does not exist in the storage.

        Example usage:
            collection = storage_instance.get_collection("123")
            if collection:
                print(collection.name)
        """
        return self._collections.get(collection_id)

    def get_all_collections(self) -> list[Collection]:
        """Retrieves all collections from storage.

        Returns:
            List[Collection]: A list of all Collection objects stored.

        Raises:
            None

        Example usage:
            collections = storage_instance.get_all_collections()
        """
        return list(self._collections.values())

    def delete_collection(self, collection_id: str) -> bool:
        """Deletes a collection by its identifier.

        Args:
            collection_id (str): The unique identifier of the collection to be deleted.

        Returns:
            bool: True if the collection was successfully deleted, False otherwise.

        Raises:
            KeyError: If the collection_id does not exist in the collections.

        Example:
            storage = Storage()
            result = storage.delete_collection(collection_id)
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False

    def get_prompts_by_collection(self, collection_id: str) -> list[Prompt]:
        """Retrieves a list of prompts associated with a given collection ID.

        Args:
            collection_id (int): The ID of the collection to filter prompts by.

        Returns:
            list: A list of prompts that belong to the specified collection.

        Raises:
            KeyError: If the collection_id does not exist in the prompts.

        Example:
            storage = Storage()
            storage.get_prompts_by_collection(1)
            [<Prompt object>, <Prompt object>]
        """
        return [
            p for p in self._prompts.values()
            if p.collection_id == collection_id
        ]

    # ============== Utility ==============

    def clear(self) -> None:
        """Clears all stored prompts and collections.

        This method removes all entries from both the internal prompts
        and collections storage, effectively resetting them to their
        initial state.

        Example:
            storage = Storage()
            storage.clear()
        """
        self._prompts.clear()
        self._collections.clear()
        self._prompt_versions.clear()


# Global storage instance
storage = Storage()
