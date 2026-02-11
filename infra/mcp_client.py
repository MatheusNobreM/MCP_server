from __future__ import annotations

import json
from typing import Any, Dict

from mcp import ClientSession
from mcp.types import TextContent


def _parse_json_text(value: str) -> Any:
    text = value.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}


async def call_mcp_tool(session: ClientSession, name: str, args: Dict[str, Any]) -> Any:
    result = await session.call_tool(name, arguments=args)

    payload = result.structuredContent
    if payload is not None:
        return payload

    texts = [
        block.text if isinstance(block, TextContent) else str(block)
        for block in result.content
    ]
    if not texts:
        return {}
    if len(texts) == 1:
        return _parse_json_text(texts[0])

    return _parse_json_text("\n".join(texts))


def to_tool_payload(tool_name: str, tool_result: Any) -> Dict[str, Any]:
    return {
        "role": "tool",
        "tool_name": tool_name,
        "content": json.dumps(tool_result, ensure_ascii=False),
    }
