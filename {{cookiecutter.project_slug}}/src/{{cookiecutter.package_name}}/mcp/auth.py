from typing import Any
import secrets
import time

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(description="Issued access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token lifetime in seconds")
    scope: str = Field(default="", description="Granted scopes as space-separated string")


class ClientRegistrationRequest(BaseModel):
    redirect_uris: list[str] | None = Field(
        default=None,
        description="Redirection URIs that the client may use in requests to the authorization server",
    )
    client_name: str | None = Field(
        default=None,
        description="Human-readable name of the client to be presented to the end-user",
    )
    token_endpoint_auth_method: str | None = Field(
        default=None,
        description="Requested authentication method for the token endpoint",
    )
    grant_types: list[str] | None = Field(
        default=None,
        description="OAuth 2.0 grant types that the client will use",
    )
    response_types: list[str] | None = Field(
        default=None,
        description="OAuth 2.0 response types that the client will use",
    )
    scope: str | None = Field(
        default=None,
        description="Space-separated list of scope values that the client can use",
    )
    jwks_uri: str | None = Field(
        default=None,
        description="URL for the client's JSON Web Key Set (JWKS) document",
    )


class ClientRegistrationResponse(BaseModel):
    client_id: str = Field(description="Unique identifier for the registered client")
    client_secret: str | None = Field(
        default=None,
        description="Client secret issued to the client, if applicable",
    )
    client_id_issued_at: int = Field(
        description="Time at which the client identifier was issued, in seconds since the Unix epoch",
    )
    client_secret_expires_at: int = Field(
        description="Time at which the client secret will expire, or 0 if it will not expire",
    )
    registration_access_token: str = Field(
        description="Access token that can be used to manage the client registration",
    )
    registration_client_uri: str = Field(
        description="Location of the client configuration endpoint",
    )
    redirect_uris: list[str] | None = None
    client_name: str | None = None
    token_endpoint_auth_method: str | None = None
    grant_types: list[str] | None = None
    response_types: list[str] | None = None
    scope: str | None = None
    jwks_uri: str | None = None


def get_oauth2_router() -> APIRouter:
    """Create a simple, overridable OAuth2 router.

    This implementation is intentionally minimal and is meant to be replaced
    or extended in real projects. It provides:

    - GET /auth/authorize
    - POST /auth/token
    - POST /auth/register (RFC 7591 dynamic client registration)
    """
    router = APIRouter()

    @router.get("/auth/authorize")
    async def authorize(
        response_type: str = "code",
        client_id: str | None = None,
        redirect_uri: str | None = None,
        scope: str | None = None,
        state: str | None = None,
    ):
        """Very simple authorization endpoint.

        For the template, this endpoint immediately redirects back to the
        provided redirect_uri with a static authorization code. Projects
        should replace this behaviour with a real login and consent flow.
        """
        if response_type != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported response_type",
            )

        if redirect_uri is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="redirect_uri is required",
            )

        query_parts: list[str] = ["code=dummy-code"]
        if state is not None:
            query_parts.append(f"state={state}")
        if scope is not None:
            query_parts.append(f"scope={scope}")

        separator = "&" if "?" in redirect_uri else "?"
        redirect_target = f"{redirect_uri}{separator}{'&'.join(query_parts)}"

        return RedirectResponse(url=redirect_target)

    @router.post("/auth/token", response_model=TokenResponse)
    async def token(
        grant_type: str = Form(...),
        code: str | None = Form(default=None),
        redirect_uri: str | None = Form(default=None),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
        scope: str | None = Form(default=None),
    ) -> TokenResponse:
        """Very simple token endpoint.

        The default implementation accepts any request and issues a static
        access token. Projects should replace this with real token issuance
        backed by an identity provider.
        """
        allowed_grant_types: set[str] = {"authorization_code", "client_credentials"}
        if grant_type not in allowed_grant_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported grant_type",
            )

        if grant_type == "authorization_code" and not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="code is required for authorization_code grant",
            )

        granted_scope = scope or ""
        token_value = "dummy-access-token"

        return TokenResponse(
            access_token=token_value,
            scope=granted_scope,
        )

    @router.post(
        "/auth/register",
        response_model=ClientRegistrationResponse,
        name="oauth_dynamic_client_registration",
        status_code=status.HTTP_201_CREATED,
    )
    async def register_client(
        request: Request,
        registration: ClientRegistrationRequest,
    ) -> ClientRegistrationResponse:
        """Dynamic client registration endpoint following RFC 7591.

        The default implementation issues opaque identifiers and does not persist
        registrations. Projects should replace this with real storage and policy.
        """
        issued_at = int(time.time())
        client_id = secrets.token_urlsafe(24)
        client_secret = secrets.token_urlsafe(32)
        registration_access_token = secrets.token_urlsafe(32)

        registration_client_uri = str(
            request.url_for("oauth_dynamic_client_registration")
        )

        return ClientRegistrationResponse(
            client_id=client_id,
            client_secret=client_secret,
            client_id_issued_at=issued_at,
            client_secret_expires_at=0,
            registration_access_token=registration_access_token,
            registration_client_uri=registration_client_uri,
            redirect_uris=registration.redirect_uris,
            client_name=registration.client_name,
            token_endpoint_auth_method=registration.token_endpoint_auth_method,
            grant_types=registration.grant_types,
            response_types=registration.response_types,
            scope=registration.scope,
            jwks_uri=registration.jwks_uri,
        )

    return router

