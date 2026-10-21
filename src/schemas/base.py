"""Shared strict API types; independent of feature request schemas."""
from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResponseMeta(APIModel):
    request_id: str
