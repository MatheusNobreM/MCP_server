from __future__ import annotations

from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FunctionCall(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    name: str
    arguments: Union[Dict[str, Any], str, None] = None


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    function: FunctionCall


class OllamaMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    role: str = "assistant"
    content: str = ""
    tool_calls: List[ToolCall] = Field(default_factory=list)

    @field_validator("tool_calls", mode="before")
    @classmethod
    def _coerce_tool_calls(cls, value: Any) -> Any:
        # Some Ollama responses send null when there are no tool calls.
        return [] if value is None else value


class OllamaResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attributes=True)

    message: OllamaMessage
