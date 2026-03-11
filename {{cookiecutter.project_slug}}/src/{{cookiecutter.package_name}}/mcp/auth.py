from typing import Any

from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(description="Issued access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token lifetime in seconds")
    scope: str = Field(default="", description="Granted scopes as space-separated string")


def get_oauth2_router() -> APIRouter:
    """Create a simple, overridable OAuth2 router.

    This implementation is intentionally minimal and is meant to be replaced
    or extended in real projects. It provides:

    - GET /oauth/authorize
    - POST /oauth/token
    """
    router = APIRouter()

    @router.get("/oauth/authorize")
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

    @router.post("/oauth/token", response_model=TokenResponse)
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

    return router

