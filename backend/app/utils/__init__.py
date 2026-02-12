"""Utility functions."""

import json
from datetime import datetime


def to_dict(obj):
    """Convert object to dictionary."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat() if dt else None


def serialize_json(obj):
    """Serialize object to JSON."""
    return json.dumps(obj, default=str, indent=2)
