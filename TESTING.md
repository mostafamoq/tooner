# Testing the Tooner Hook

## About the Hook

The Tooner hook uses the **official toon-python library** for compression. The library is automatically installed by the installation script.

## Understanding Hook Input Format

The Tooner hook is designed to work with Claude Code's hook system. Claude Code sends input to hooks in a specific JSON format:

```json
{
  "prompt": "your actual prompt text here"
}
```

## Testing Methods

### ✅ Method 1: Test in Claude Code (Recommended)

This is the **real-world test** - just use Claude Code normally:

1. Start Claude Code
2. Paste this prompt:
   ```
   Analyze this data:
   [
     {"id": 1, "name": "Alice", "email": "alice@example.com"},
     {"id": 2, "name": "Bob", "email": "bob@example.com"},
     {"id": 3, "name": "Carol", "email": "carol@example.com"}
   ]
   ```
3. You should see a message about compression!

### ✅ Method 2: Manual Command Line Test

If you want to test the hook manually from the command line, you need to send the **same format** Claude Code uses:

```bash
# Correct format (with escaped quotes)
printf '{"prompt": "Analyze [{\\"id\\": 1, \\"name\\": \\"Alice\\"}, {\\"id\\": 2, \\"name\\": \\"Bob\\"}, {\\"id\\": 3, \\"name\\": \\"Carol\\"}]"}' | ~/.claude/hooks/compress_prompt.py
```

**Expected output:**
```
Analyze
[AUTOMATICALLY COMPRESSED BY TOONER HOOK]
Original: 31 tokens → Compressed: 10 tokens (Saved 21 tokens)

data[3]{id,name}:
 1,Alice
 2,Bob
 3,Carol

[Note: This data was automatically compressed from JSON to Toon format to save tokens]
```

### ❌ Common Mistake

**This will NOT work:**
```bash
# Wrong - missing the JSON wrapper
echo 'Test prompt with [{"id": 1}]' | ~/.claude/hooks/compress_prompt.py
# Error: Expecting value: line 1 column 1 (char 0)
```

The hook expects the `{"prompt": "..."}` wrapper because that's how Claude Code calls it.

## Monitoring Hook Activity

Watch the log file to see what the hook is doing:

```bash
# Clear log and watch in real-time
> ~/.claude/tooner_hook.log
tail -f ~/.claude/tooner_hook.log
```

## What Gets Compressed?

The hook will **only** compress JSON arrays that meet these criteria:

- ✅ Array has **3 or more** items
- ✅ All items are **objects with the same fields** (uniform)
- ✅ Compression saves **more than 30%** tokens

**Examples:**

| Input | Will Compress? | Reason |
|-------|---------------|--------|
| `[{"id": 1}]` | ❌ No | Only 1 item (needs 3+) |
| `[{"id": 1}, {"id": 2}]` | ❌ No | Only 2 items (needs 3+) |
| `[{"id": 1}, {"id": 2}, {"id": 3}]` | ✅ Yes | 3 items, uniform, saves tokens |
| `[{"id": 1}, {"name": "Alice"}]` | ❌ No | Not uniform (different fields) |

## Troubleshooting

### Hook not working in Claude Code?

1. **Check file exists:**
   ```bash
   ls -la ~/.claude/hooks/compress_prompt.py
   ```

2. **Check permissions:**
   ```bash
   chmod +x ~/.claude/hooks/compress_prompt.py
   ```

3. **Verify settings.json:**
   ```bash
   cat ~/.claude/settings.json
   ```

4. **Check logs:**
   ```bash
   tail -20 ~/.claude/tooner_hook.log
   ```

### Manual test fails?

Make sure you're using `printf` with properly escaped quotes:
```bash
printf '{"prompt": "Test [{\\"id\\": 1}, {\\"id\\": 2}, {\\"id\\": 3}]"}' | ~/.claude/hooks/compress_prompt.py
```

## Success Indicators

When the hook is working correctly, you'll see:

1. **In Claude Code:** A message like `[AUTOMATICALLY COMPRESSED BY TOONER HOOK]` in your prompt
2. **In logs:** Entries showing compression activity
3. **In output:** Token savings statistics

---

**Need help?** Open an issue at https://github.com/mostafamoq/tooner/issues
