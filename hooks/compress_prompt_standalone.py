#!/usr/bin/env python3
"""
Claude Code Hook: UserPromptSubmit - Auto-compress JSON before LLM

This hook intercepts user prompts BEFORE they reach the LLM.
When it detects JSON data, it automatically compresses it to Toon format.

This is a STANDALONE version with no external dependencies.
"""

import json
import sys
import re
from pathlib import Path
from typing import Any, Union, List, Dict, Tuple


# ============================================================================
# EMBEDDED FUNCTIONS FROM tooner.server (no external dependencies needed)
# ============================================================================

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation (approx 1 token per 4 characters for English text).
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


# ============================================================================
# HOOK LOGIC
# ============================================================================

def detect_json_in_text(text: str) -> List[Tuple[int, int, Any]]:
    """
    Detect and extract JSON data from text.

    Returns:
        list of tuples: [(start_pos, end_pos, json_data), ...]
    """
    json_blocks = []

    # Pattern 1: Look for array patterns
    array_pattern = r'\[\s*\{[^\]]+\}\s*(?:,\s*\{[^\]]+\}\s*)*\]'
    for match in re.finditer(array_pattern, text, re.DOTALL):
        try:
            data = json.loads(match.group())
            json_blocks.append((match.start(), match.end(), data))
        except:
            continue

    # Pattern 2: Look for object patterns
    if not json_blocks:
        obj_pattern = r'\{[^\}]+\}'
        for match in re.finditer(obj_pattern, text, re.DOTALL):
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and len(data) > 2:
                    json_blocks.append((match.start(), match.end(), data))
            except:
                continue

    return json_blocks


def should_compress(data: Any, min_items: int = 3) -> bool:
    """
    Determine if data should be compressed.

    Args:
        data: JSON data
        min_items: Minimum array items to consider compression

    Returns:
        bool: True if compression would be beneficial
    """
    if not isinstance(data, list):
        return False

    if len(data) < min_items:
        return False

    if not is_uniform_array(data):
        return False

    # Calculate potential savings
    json_str = json.dumps(data)
    toon_str = json_to_toon(data)

    json_tokens = estimate_tokens(json_str)
    toon_tokens = estimate_tokens(toon_str)

    savings_percent = ((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens > 0 else 0

    # Only compress if savings > 30%
    return savings_percent > 30


def compress_prompt(prompt_text: str, min_items: int = 3) -> Tuple[str, bool, Dict]:
    """
    Compress JSON in prompt to Toon format.

    Args:
        prompt_text: Original prompt text
        min_items: Minimum items to trigger compression

    Returns:
        tuple: (modified_text, was_compressed, stats)
    """
    json_blocks = detect_json_in_text(prompt_text)

    if not json_blocks:
        return prompt_text, False, {}

    # Process blocks in reverse order to maintain positions
    modified_text = prompt_text
    compressed_count = 0
    total_savings = 0

    for start, end, data in reversed(json_blocks):
        if should_compress(data):
            # Compress to Toon
            toon_output = json_to_toon(data, name="data")

            # Calculate savings
            original = json.dumps(data, indent=2)
            original_tokens = estimate_tokens(original)
            toon_tokens = estimate_tokens(toon_output)
            savings = original_tokens - toon_tokens

            # Add explanation
            compressed_text = f"""
[AUTOMATICALLY COMPRESSED BY TOONER HOOK]
Original: {original_tokens} tokens → Compressed: {toon_tokens} tokens (Saved {savings} tokens)

{toon_output}

[Note: This data was automatically compressed from JSON to Toon format to save tokens]
"""

            # Replace in text
            modified_text = modified_text[:start] + compressed_text + modified_text[end:]
            compressed_count += 1
            total_savings += savings

    stats = {
        "compressed_blocks": compressed_count,
        "total_tokens_saved": total_savings
    }

    return modified_text, compressed_count > 0, stats


def log_to_file(message: str, log_file: Path = Path.home() / ".claude" / "tooner_hook.log"):
    """
    Log message to file for debugging.

    Args:
        message: Message to log
        log_file: Path to log file
    """
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        # Silently fail if logging doesn't work
        pass


def main():
    """
    Main hook entry point.

    Reads prompt from stdin, compresses JSON if found, outputs modified prompt.
    """
    try:
        # Read hook input
        input_data = json.load(sys.stdin)

        # Get the prompt
        original_prompt = input_data.get("prompt", "")

        if not original_prompt:
            # No prompt to process
            log_to_file("No prompt found in input")
            sys.exit(0)

        # Try to compress JSON in the prompt
        modified_prompt, was_compressed, stats = compress_prompt(original_prompt)

        if was_compressed:
            # Log to file
            log_msg = f"Compressed {stats['compressed_blocks']} JSON blocks, saved {stats['total_tokens_saved']} tokens"
            log_to_file(log_msg)

            # Log to stderr (visible in debug logs)
            print(f"[Tooner Hook] {log_msg}", file=sys.stderr)

            # Output modified prompt
            print(modified_prompt)
            sys.exit(0)
        else:
            # No compression needed, pass through
            log_to_file("No compressible JSON found")
            sys.exit(0)

    except Exception as e:
        # Log error but don't block
        error_msg = f"Error: {e}"
        log_to_file(error_msg)
        print(f"[Tooner Hook] {error_msg}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
