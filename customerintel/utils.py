"""Shared utilities for response parsing."""

import json
import re


def parse_json_response(text: str, fallback=None):
    """
    Parse JSON from a text response that may contain markdown code fences.

    Attempts json.loads on the raw text, then on text with fences stripped,
    then uses a greedy regex to find the first JSON object or array.
    Returns `fallback` if all attempts fail.
    """
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", text).strip()
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()

    for candidate in (text.strip(), cleaned):
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            pass

    # Last resort: grab first balanced JSON object or array
    for pattern in (r"\{.*\}", r"\[.*\]"):
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass

    return fallback
