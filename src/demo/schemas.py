"""Strict landing-page conversation contract."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictStr, field_validator

MAX_DEMO_BODY_BYTES = 20 * 1024


class DemoMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    role: Literal["user", "assistant"]
    content: StrictStr

    @field_validator("content")
    @classmethod
    def nonempty_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Tin nhắn không được để trống.")
        return value


class DemoChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    messages: list[DemoMessage]

    @field_validator("messages")
    @classmethod
    def normalize_conversation(cls, messages: list[DemoMessage]) -> list[DemoMessage]:
        if not messages or messages[0].role != "user" or messages[-1].role != "user":
            raise ValueError("Tin đầu và tin cuối phải là tin nhắn người dùng.")
        for message in messages:
            if message.role == "user" and len(message.content) > 500:
                raise ValueError("Tin nhắn người dùng tối đa 500 ký tự.")
            if message.role == "assistant":
                message.content = message.content[:2000]
        recent = messages[-10:]
        # A truncated alternating conversation can start with an assistant.
        # Drop the orphaned reply while keeping chronological order and <= 10 turns.
        while recent[0].role != "user":
            recent = recent[1:]
        return recent


class DemoChatResponse(BaseModel):
    reply: str
    mode: Literal["demo"] = "demo"


class DemoErrorResponse(BaseModel):
    error: str


class DemoConfigResponse(BaseModel):
    botName: str
    welcome: str
    suggestions: list[str]
    loginUrl: str
    signupUrl: str
