#!/usr/bin/env python3
"""Tooner MCP Test Server - Test/demo server for exploring Toon compression tools.

This MCP server is for testing and exploration only.
For production use, install the Tooner hook for Claude Code instead.
"""

import json
from typing import Any, Dict, List, Union
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("tooner")


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation (approx 1 token per 4 characters for English text).
    For more accurate counting, integrate with tiktoken library.
    """
    return len(text) // 4


def is_uniform_array(data: Any) -> bool:
    """
    Check if data is a uniform array of objects (ideal for Toon compression).

    Args:
        data: The data structure to analyze

    Returns:
        True if data is a uniform array suitable for Toon compression
    """
    if not isinstance(data, list) or len(data) == 0:
        return False

    if not all(isinstance(item, dict) for item in data):
        return False

    # Check if all objects have the same keys
    if len(data) == 0:
        return False

    first_keys = set(data[0].keys())
    return all(set(item.keys()) == first_keys for item in data)


def json_to_toon(data: Union[Dict, List], name: str = "data") -> str:
    """
    Convert JSON data to Toon format.

    Args:
        data: JSON data (dict or list)
        name: Name for the data structure

    Returns:
        Toon formatted string
    """
    if isinstance(data, dict):
        # If it's a dict with a single array key, use that
        if len(data) == 1:
            key = list(data.keys())[0]
            if isinstance(data[key], list):
                return json_to_toon(data[key], name=key)

        # Otherwise convert dict to single-row format
        keys = list(data.keys())
        values = [data[k] for k in keys]
        return f"{name}[1]{{{','.join(keys)}}}:\n {','.join(str(v) for v in values)}"

    if isinstance(data, list) and len(data) > 0:
        if not is_uniform_array(data):
            # Fallback to JSON for non-uniform data
            return json.dumps(data, indent=2)

        # Uniform array - perfect for Toon
        keys = list(data[0].keys())
        rows = []

        for item in data:
            values = [item.get(k, '') for k in keys]
            # Escape commas in values and quote if necessary
            formatted_values = []
            for v in values:
                v_str = str(v)
                if ',' in v_str or ' ' in v_str or '\n' in v_str:
                    v_str = f'"{v_str}"'
                formatted_values.append(v_str)
            rows.append(' ' + ','.join(formatted_values))

        header = f"{name}[{len(data)}]{{{','.join(keys)}}}:"
        return header + '\n' + '\n'.join(rows)

    # Fallback for other types
    return json.dumps(data, indent=2)


def toon_to_json(toon_str: str) -> Union[Dict, List]:
    """
    Convert Toon format back to JSON.

    Args:
        toon_str: Toon formatted string

    Returns:
        JSON data (dict or list)
    """
    lines = toon_str.strip().split('\n')
    if len(lines) == 0:
        return {}

    # Parse header: name[count]{fields}:
    header = lines[0]
    if '{' not in header or '}' not in header:
        # Not valid Toon format, try parsing as JSON
        try:
            return json.loads(toon_str)
        except json.JSONDecodeError:
            return {"error": "Invalid Toon format"}

    # Extract fields
    fields_start = header.index('{') + 1
    fields_end = header.index('}')
    fields = [f.strip() for f in header[fields_start:fields_end].split(',')]

    # Parse data rows
    result = []
    for line in lines[1:]:
        if not line.strip():
            continue

        # Simple CSV parsing (handles basic quoted values)
        values = []
        current = ""
        in_quotes = False

        for char in line.strip():
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                values.append(current.strip())
                current = ""
            else:
                current += char

        if current:
            values.append(current.strip())

        # Create object
        if len(values) == len(fields):
            obj = {}
            for i, field in enumerate(fields):
                value = values[i]
                # Try to convert to int/float if possible
                try:
                    if '.' in value:
                        obj[field] = float(value)
                    else:
                        obj[field] = int(value)
                except ValueError:
                    obj[field] = value
            result.append(obj)

    return result


@mcp.tool()
def compress_to_toon(data: Union[Dict, List], name: str = "data") -> Dict[str, Any]:
    """
    Convert JSON data to Toon format to reduce token usage.

    Best for uniform arrays of objects with consistent fields.
    Can achieve up to 40% token reduction on suitable data.

    Args:
        data: JSON data to compress (dict or list)
        name: Optional name for the data structure (default: "data")

    Returns:
        Dict containing:
        - toon: The compressed Toon format string
        - original_tokens: Estimated token count for original JSON
        - toon_tokens: Estimated token count for Toon format
        - savings_percent: Percentage of tokens saved
        - is_uniform: Whether data is uniform (ideal for Toon)
    """
    original_json = json.dumps(data, indent=2)
    original_tokens = estimate_tokens(original_json)

    toon_output = json_to_toon(data, name)
    toon_tokens = estimate_tokens(toon_output)

    savings = ((original_tokens - toon_tokens) / original_tokens * 100) if original_tokens > 0 else 0

    return {
        "toon": toon_output,
        "original_tokens": original_tokens,
        "toon_tokens": toon_tokens,
        "savings_percent": round(savings, 2),
        "is_uniform": is_uniform_array(data) if isinstance(data, list) else False
    }


@mcp.tool()
def parse_from_toon(toon_str: str) -> Dict[str, Any]:
    """
    Convert Toon format back to JSON.

    Parses Toon formatted data and returns standard JSON structure.

    Args:
        toon_str: String in Toon format

    Returns:
        Dict containing:
        - json: The parsed JSON data
        - success: Whether parsing was successful
    """
    try:
        parsed_data = toon_to_json(toon_str)
        return {
            "json": parsed_data,
            "success": True
        }
    except Exception as e:
        return {
            "json": None,
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def compare_token_usage(data: Union[Dict, List], name: str = "data") -> Dict[str, Any]:
    """
    Compare token usage between JSON and Toon formats.

    Analyzes the data structure and provides detailed comparison
    of token usage between standard JSON and Toon format.

    Args:
        data: JSON data to analyze
        name: Optional name for the data structure

    Returns:
        Dict containing:
        - json_format: The JSON string
        - toon_format: The Toon string
        - json_tokens: Token count for JSON
        - toon_tokens: Token count for Toon
        - savings_tokens: Absolute token savings
        - savings_percent: Percentage savings
        - recommendation: Whether to use Toon for this data
    """
    json_str = json.dumps(data, indent=2)
    json_tokens = estimate_tokens(json_str)

    toon_str = json_to_toon(data, name)
    toon_tokens = estimate_tokens(toon_str)

    savings_tokens = json_tokens - toon_tokens
    savings_percent = (savings_tokens / json_tokens * 100) if json_tokens > 0 else 0

    is_uniform = is_uniform_array(data) if isinstance(data, list) else False
    recommendation = "Use Toon" if is_uniform and savings_percent > 10 else "Use JSON"

    return {
        "json_format": json_str,
        "toon_format": toon_str,
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings_tokens": savings_tokens,
        "savings_percent": round(savings_percent, 2),
        "is_uniform": is_uniform,
        "recommendation": recommendation
    }


@mcp.tool()
def should_use_toon(data: Union[Dict, List]) -> Dict[str, Any]:
    """
    Analyze data structure to determine if Toon compression would be beneficial.

    Provides recommendations on whether to use Toon format based on
    data structure characteristics and potential token savings.

    Args:
        data: JSON data to analyze

    Returns:
        Dict containing:
        - should_use: Boolean recommendation
        - is_uniform: Whether data is uniform array
        - estimated_savings_percent: Expected token savings
        - reason: Explanation of recommendation
    """
    if not isinstance(data, list):
        return {
            "should_use": False,
            "is_uniform": False,
            "estimated_savings_percent": 0,
            "reason": "Toon works best with arrays of uniform objects. This is not an array."
        }

    if len(data) == 0:
        return {
            "should_use": False,
            "is_uniform": False,
            "estimated_savings_percent": 0,
            "reason": "Array is empty."
        }

    uniform = is_uniform_array(data)

    if not uniform:
        return {
            "should_use": False,
            "is_uniform": False,
            "estimated_savings_percent": 0,
            "reason": "Array objects have inconsistent fields. Toon requires uniform structure."
        }

    # Calculate estimated savings
    json_str = json.dumps(data, indent=2)
    toon_str = json_to_toon(data)

    json_tokens = estimate_tokens(json_str)
    toon_tokens = estimate_tokens(toon_str)

    savings_percent = ((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens > 0 else 0

    should_use = savings_percent > 10  # Recommend if savings > 10%

    reason = f"Uniform array with {len(data)} items. " + \
             f"Expected savings: ~{round(savings_percent, 1)}%. " + \
             ("Recommended for token efficiency." if should_use else "Minimal benefit.")

    return {
        "should_use": should_use,
        "is_uniform": True,
        "estimated_savings_percent": round(savings_percent, 2),
        "reason": reason,
        "array_size": len(data),
        "field_count": len(data[0].keys()) if len(data) > 0 else 0
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
