# API Reference - Endpoints Overview:

## Health Check Endpoint

### `GET /health`
**Description:**
Checks the health status of the application.

- **Request:** None
- **Response:**
  ```json
  {
    "status": "healthy",
    "version": "<version>"
  }
  ```
- **Error Response:** None
- **Authentication:** None

---

## Prompt Endpoints

### `GET /prompts`
**Description:**
Retrieve a list of prompts, optionally filtered by collection and search query.
- **Request:**
  - Query Parameters:
    - `collection_id` (Optional): The ID of the collection to filter prompts by.
    - `search` (Optional): A search query to filter prompts.
- **Response:**
  ```json
  {
    "prompts": [
      {/* prompt data */},
      {/* more prompts */}
    ],
    "total": <total_count>
  }
  ```
- **Error Response:**
  - **400 Bad Request**: "ValueError"
- **Authentication:** None

### `GET /prompts/{prompt_id}`
**Description:**
Retrieve a prompt by its ID.
- **Request:**
  - Path Parameter: `prompt_id` (string) - The unique identifier for the prompt.
- **Response:**
  ```json
  {
    /* prompt data */
  }
  ```
- **Error Response:**
  - **404 Not Found**: "Prompt not found"
- **Authentication:** None

### `POST /prompts`
**Description:**
Create a new prompt and store it in the database.
- **Request:**
  - Request Body: `PromptCreate` object containing necessary data.
- **Response:**
  ```json
  {
    /* new prompt data */
  }
  ```
- **Error Response:**
  - **400 Bad Request**: "Collection not found"
- **Authentication:** None

### `PUT /prompts/{prompt_id}`
**Description:**
Update an existing prompt with new data.
- **Request:**
  - Path Parameter: `prompt_id` (string) - The unique identifier of the prompt to update.
  - Request Body: `PromptUpdate` object with updated data.
- **Response:**
  ```json
  {
    /* updated prompt data */
  }
  ```
- **Error Response:**
  - **404 Not Found**: "Prompt not found"
  - **400 Bad Request**: "Collection not found"
- **Authentication:** None

### `PATCH /prompts/{prompt_id}`
**Description:**
Partially update an existing prompt with new data fields.
- **Request:**
  - Path Parameter: `prompt_id` (string) - The identifier of the prompt to update.
  - Request Body: `PromptPatch` object with data fields to update.
- **Response:**
  ```json
  {
    /* updated prompt data */
  }
  ```
- **Error Response:**
  - **404 Not Found**: "Prompt not found"
  - **400 Bad Request**: "No fields provided for update"
  - **400 Bad Request**: "Collection not found"
- **Authentication:** None

### `DELETE /prompts/{prompt_id}`
**Description:**
Deletes a prompt by its ID.
- **Request:**
  - Path Parameter: `prompt_id` (string) - The unique identifier of the prompt to be deleted.
- **Response:** None
- **Error Response:**
  - **404 Not Found**: "Prompt not found"
- **Authentication:** None

---

## Collection Endpoints

### `GET /collections`
**Description:**
Retrieve a list of all collections.
- **Request:** None
- **Response:**
  ```json
  {
    "collections": [
      {/* collection data */},
      {/* more collections */}
    ],
    "total": <total_count>
  }
  ```
- **Error Response:** None
- **Authentication:** None

### `GET /collections/{collection_id}`
**Description:**
Retrieve a specific collection by its ID.
- **Request:**
  - Path Parameter: `collection_id` (string) - The unique identifier of the collection to retrieve.
- **Response:**
  ```json
  {
    /* collection data */
  }
  ```
- **Error Response:**
  - **404 Not Found**: "Collection not found"
- **Authentication:** None

### `POST /collections`
**Description:**
Create a new collection.
- **Request:**
  - Request Body: `CollectionCreate` object with necessary data.
- **Response:**
  ```json
  {
    /* new collection data */
  }
  ```
- **Error Response:** None
- **Authentication:** None

### `DELETE /collections/{collection_id}`
**Description:**
Delete a collection and disassociate it from its prompts.
- **Request:**
  - Path Parameter: `collection_id` (string) - The unique identifier of the collection to be deleted.
- **Response:** None
- **Error Response:**
  - **404 Not Found**: "Collection not found"
- **Authentication:** None

---