from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extract a JSON object from model output.

    Structured output should return clean JSON. This helper is a fallback for
    weaker local models that sometimes wrap JSON in extra text.
    """
    cleaned = text.strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response.")

    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Extracted JSON was not an object.")

    return data
