import os
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Dict, Any, Optional
from jose.exceptions import JWTError
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException, Path, status
# 
#  JWKS  json web key set, public URL that returns the public keys used to verify JWT signatures.
# -----------------------------
TENANT_ID = os.getenv("ENTRA_TENANT_ID")
API_AUDIENCE = os.getenv("ENTRA_API_AUDIENCE")  # or the API app client_id
SWAGGER_CLIENT_ID = os.getenv("ENTRA_SWAGGER_CLIENT_ID") 

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
OIDC_CONFIG_URL = f"{AUTHORITY}/.well-known/openid-configuration"
SCOPE_NAME = os.getenv("ENTRA_SCOPE_NAME", "access_as_user")  # scope you created under "Expose an API"
SCOPES = {f"{API_AUDIENCE}/{SCOPE_NAME}": "Access the API"}

_AUTHORIZATION_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL         = f"{AUTHORITY}/oauth2/v2.0/token"
ISSUER            = f"{AUTHORITY}"  # for v2 tokens, issuer typically matches metadata; verify in your tokens
JWKS_URI          = f"{AUTHORITY}/discovery/v2.0/keys"

# Keep JWKS caching (keys rotate)  JSON WEB KEY SET. 
_jwks_cache : Dict[str, Any] = {"keys": None, "expires_at": 0}
_oidc_cache : Dict[str, Any] = {}

import time, requests
def get_jwks():
    now = int(time.time())
    if _jwks_cache["keys"] and now < _jwks_cache["expires_at"]:
        return _jwks_cache["keys"]
    
    jwks= requests.get(JWKS_URI, timeout=10).json()
    _jwks_cache["keys"] = jwks 
    _jwks_cache["expires_at"] = now + 6 * 3600
    return jwks

def get_oidc_config() -> Dict[str, Any]:
    if _oidc_cache:
        return _oidc_cache
    cfg = requests.get(OIDC_CONFIG_URL, timeout=10).json()
    _oidc_cache.update(cfg)
    return _oidc_cache

## oauth2 schema for Swagger UI "Authorize" button
oauth2_schema = OAuth2AuthorizationCodeBearer(
    authorizationUrl=_AUTHORIZATION_URL,
    tokenUrl=TOKEN_URL,
    scopes=SCOPES,
    auto_error=True,
)

def validate_entra_jwt(token: str) -> Optional[Dict[str, Any]]:
    cfg = get_oidc_config()
    jwks = get_jwks()
    issuer= cfg["issuer"]
    try:
        claims = jwt.decode(
            token, jwks, 
            algorithms=["RS256"], audience=API_AUDIENCE, issuer=issuer,
            options={"verigy_aud": True, "verify_iss": True}
        )
        return claims
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e), headers={"WWW-Authenticate": "Bearer"})