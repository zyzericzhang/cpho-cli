from __future__ import annotations

import json
import re
from typing import Any


_FENCED_JSON_RE = re.compile(r"^\s*```(?:json|JSON)?\s*(?P<body>.*?)\s*```\s*$", re.DOTALL)


def extract_json_text(value: str) -> str:
    text = value.strip()
    match = _FENCED_JSON_RE.match(text)
    if match is not None:
        return match.group("body").strip()
    return text


def loads_json_object(value: str) -> dict[str, Any]:
    data = json.loads(extract_json_text(value))
    if not isinstance(data, dict):
        raise ValueError("JSON response must be an object")
    return data

