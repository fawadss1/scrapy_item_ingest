"""
Serialization utilities for converting data to JSON-serializable format.
"""
import json
from datetime import datetime, date, time
from decimal import Decimal


def serialize_stats(obj):
    """Recursively convert stats to JSON-serializable format"""
    if isinstance(obj, dict):
        return {key: serialize_stats(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_stats(item) for item in obj]
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        # For any other type, convert to string
        return str(obj)


def serialize_item_data(item_dict):
    """Serialize item data to JSON string"""
    return json.dumps(item_dict, ensure_ascii=False, default=str)
