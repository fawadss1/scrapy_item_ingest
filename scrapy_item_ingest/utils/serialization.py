"""
Serialization utilities for converting data to JSON-serializable format.
"""
import json


def serialize_item_data(item_dict):
    """Serialize item data to JSON string"""
    return json.dumps(item_dict, ensure_ascii=False, default=str)
