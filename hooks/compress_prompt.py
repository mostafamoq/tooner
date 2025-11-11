#!/usr/bin/env python3
"""
Claude Code Hook: UserPromptSubmit - Auto-compress JSON before LLM

This hook intercepts user prompts BEFORE they reach the LLM.
When it detects JSON data, it automatically compresses it to Toon format.

This is the REAL solution for saving tokens on the first LLM call!
"""

import json
import sys
import re
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tooner.server import json_to_toon, estimate_tokens, is_uniform_array


def detect_json_in_text(text: str):
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


def should_compress(data, min_items=3):
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


def compress_prompt(prompt_text: str, min_items=3):
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
            sys.exit(0)

        # Try to compress JSON in the prompt
        modified_prompt, was_compressed, stats = compress_prompt(original_prompt)

        if was_compressed:
            # Log to stderr (visible in debug logs)
            print(f"[Tooner Hook] Compressed {stats['compressed_blocks']} JSON blocks", file=sys.stderr)
            print(f"[Tooner Hook] Saved {stats['total_tokens_saved']} tokens", file=sys.stderr)

            # Output modified prompt
            print(modified_prompt)
            sys.exit(0)
        else:
            # No compression needed, pass through
            sys.exit(0)

    except Exception as e:
        # Log error but don't block
        print(f"[Tooner Hook] Error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
