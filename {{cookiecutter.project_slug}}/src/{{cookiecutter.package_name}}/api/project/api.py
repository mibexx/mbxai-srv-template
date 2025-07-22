"""Project-level API endpoints."""

from fastapi import APIRouter


# Create a router for project-level endpoints
router = APIRouter(prefix="/api", tags=["api"])
