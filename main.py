from fastapi import FastAPI, Header, HTTPException, Depends, Query
from typing import Optional, Dict
import uuid

app = FastAPI()

# In-memory store mapping friendly names to API keys
api_keys: Dict[str, str] = {}

# Dependency to verify the API key passed in the request header
def get_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key not in api_keys.values():
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return x_api_key

# --- Routes ---

@app.post("/create-key")
def create_key(name: str = Query(..., min_length=1)):
    """
    Create a new API key with a friendly name.

    Query Parameter:
    - name: A friendly name to associate with the API key (must be unique)

    Returns:
    - The friendly name and the generated API key
    """
    if name in api_keys:
        raise HTTPException(status_code=400, detail="Name already exists")
    new_key = str(uuid.uuid4())
    api_keys[name] = new_key
    return {"name": name, "api_key": new_key}


@app.get("/list-keys")
def list_keys():
    """
    List all existing friendly names associated with stored API keys.
    (The API keys themselves are not shown.)
    """
    return {"names": list(api_keys.keys())}


@app.delete("/delete-key/{name}")
def delete_key(name: str):
    """
    Delete an API key by its friendly name.

    Path Parameter:
    - name: The friendly name whose key should be deleted

    Returns:
    - Success message or 404 if not found
    """
    if name in api_keys:
        del api_keys[name]
        return {"detail": f"Deleted API key for '{name}'"}
    else:
        raise HTTPException(status_code=404, detail="API key not found")


@app.get("/public")
def public():
    """
    Public endpoint, accessible without an API key.
    """
    return {"message": "This is a public endpoint."}


@app.get("/protected")
def protected(api_key: str = Depends(get_api_key)):
    """
    Protected endpoint, requires a valid API key passed in the `X-API-Key` header.
    """
    return {"message": "You have access to the protected endpoint!"}
