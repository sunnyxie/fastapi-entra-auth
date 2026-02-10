
import datetime
from jose import jwt
from typing import Dict, Any, Optional
from datetime import datetime
from azure_auth import SCOPES, SWAGGER_CLIENT_ID, oauth2_schema, validate_entra_jwt
from jose.exceptions import JWTError
from fastapi import FastAPI, Depends, HTTPException, Path, status
from uuid import uuid4
from pydantic import Field, BaseModel


def get_current_user(claims: Dict[str, Any] = Depends(lambda token=Depends(oauth2_schema) : validate_entra_jwt(token))):
    # ' preferred_username, upn oid, scp (delegated scopes)
    return {
        'oid': claims.get("oid"),
        'name': claims.get("name"),
        'preferred_username': claims.get("preferred_username"),
        'email': claims.get("email")    ,
        'scopes': (claims.get("scp") or "").split(),
        'raw': claims
    }

## API Create / Patch / Delete
app = FastAPI(title = "items API", version = "1.1.0.0")

print(f' client ID: {SWAGGER_CLIENT_ID} ')
app.swagger_ui_init_oauth = {
    "clientId": SWAGGER_CLIENT_ID,
    "usePkceWithAuthorizationCodeGrant": True,
    "scopes": list(SCOPES.keys()),
}

# demo 
DB : dict[str, dict] = {}

class ItemCreate(BaseModel):
    name: str= Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    price: float = Field(..., ge=0)

class ItemPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)

class ItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    created_utc: str
    updated_utc: str

def now_utc() -> str:
    return datetime.utcnow().isoformat() + "Z"

@app.get("/items", response_model=list[ItemOut], tags=["items"])
def list_items(user = Depends(get_current_user)):
    return list(DB.values())

@app.get("/items/{item_id}", response_model=ItemOut, tags=["items"])
def get_item(item_id: str = Path(..., description="Item ID"),
    user = Depends(get_current_user),
):
    item = DB.get(item_id)
    return item


@app.post("/items", response_model=ItemOut, status_code=201, tags=["items"])
def create_item(payload: ItemCreate, user = Depends(get_current_user)):
    item_id = str(uuid4())
    record = {
        "id": item_id,
        "name": payload.name,
        "description": payload.description,
        "price": payload.price,
        "created_utc": now_utc(),
        "updated_utc": now_utc(),
    }
    DB[item_id] = record
    return record


@app.patch("/items/{item_id}", response_model=ItemOut, tags=["items"])
def patch_item(
    payload: ItemPatch,
    item_id: str = Path(..., description="Item ID"),
    user = Depends(get_current_user),
):
    existing = DB.get(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    update = payload.model_dump(exclude_unset=True)
    for k, v in update.items():
        existing[k] = v
    existing["updated_utc"] = now_utc()
    #DB[item_id] = existing
    return existing

@app.delete("/items/{item_id}", status_code=204, tags=["items"])
def delete_item(
    item_id: str,
    user = Depends(get_current_user),
):
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    del DB[item_id]
    return None

@app.get("/me", tags=["Auth"])
def me(user = Depends(get_current_user)):
    return user

@app.get('/secret')
def get_secret():
    MY_PASS = get_secret("ihs-bronze-secret")
    print(f"Your secret value is: {MY_PASS}")
    return 'you got the pass.'


from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
VAULT_URL = 'https://key-vault-2026-test3.vault.azure.net/'
def get_secret(secret_name):
    try:
            credential = DefaultAzureCredential()
            
            client = SecretClient(vault_url=VAULT_URL, credential=credential)

            # 4. Retrieve the secret
            retrieved_secret = client.get_secret(secret_name)
            
            return retrieved_secret.value
    except Exception as e:
        print(f"Failed to retrieve secret: {e}")
        return None