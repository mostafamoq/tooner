# Tooner - Claude Code Hook

**Reduce LLM token usage by up to 60% with automatic JSON compression**

Tooner is a Claude Code hook that automatically compresses structured JSON data into the efficient [Toon format](https://github.com/toon-format/toon) before sending to LLMs. Uses the official [toon-python library](https://github.com/toon-format/toon-python) for compression. Perfect for working with large datasets, API responses, and tabular data.

---

**📚 Quick Navigation:** [Installation](#-installation) · [Testing](#-testing-with-mcp-server-optional) · [How It Works](#-how-it-works) · [Development](#-development) · [Contributing](#-contributing)

---

## ⚡ Get Started

**Install the hook:** Follow the [installation steps](#-installation) to automatically compress JSON data in Claude Code.

**Want to test the compression first?** [Use the MCP test server](#-testing-with-mcp-server-optional) with Claude Desktop to explore how Toon compression works.

---

## 🚀 Quick Overview

**What it does:** Converts verbose JSON arrays into compact Toon format, dramatically reducing tokens.

**Example:**
```json
// Before (100 tokens)
[
  {"id": 1, "name": "Alice", "role": "admin", "status": "active"},
  {"id": 2, "name": "Bob", "role": "user", "status": "active"},
  {"id": 3, "name": "Carol", "role": "admin", "status": "inactive"}
]

// After (55 tokens) - 45% savings!
data[3]{id,name,role,status}:
 1,Alice,admin,active
 2,Bob,user,active
 3,Carol,admin,inactive
```

## 📦 Installation

### Requirements

- Python 3.8+
- pip or pipx (Python package manager)
- Claude Code CLI

**Note:** The installer automatically handles externally-managed Python environments using `pip --user`, which works on all systems.

### Automatic Installation (Recommended)

Run this one command to install everything:

```bash
curl -fsSL https://raw.githubusercontent.com/mostafamoq/tooner/main/install.sh | bash
```

Or from the repository:

```bash
git clone https://github.com/mostafamoq/tooner.git
cd tooner
./install.sh
```

**What it does:**
1. ✅ Installs the official `toon-python` library
2. ✅ Downloads and installs the hook file
3. ✅ Configures your `settings.json` automatically
4. ✅ Sets proper file permissions
5. ✅ Backs up your existing settings

**[→ Skip to Testing](#testing-the-installation)**

---

### Manual Installation

If you prefer to install manually:

#### Step 1: Install toon-python library

```bash
# Recommended: User installation (works on all systems)
pip install --user toon-python

# Or if --user doesn't work:
pip install toon-python

# Or for externally-managed environments:
pip install --break-system-packages toon-python
```

#### Step 2: Download and install the hook file
```bash
mkdir -p ~/.claude/hooks
curl -o ~/.claude/hooks/compress_prompt.py \
  https://raw.githubusercontent.com/mostafamoq/tooner/main/hooks/compress_prompt.py
chmod +x ~/.claude/hooks/compress_prompt.py
```

#### Step 3: Configure Claude Code

Edit or create `~/.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/compress_prompt.py"
          }
        ]
      }
    ]
  }
}
```

**Note:** The `~` automatically expands to your home directory.

---

### Testing the Installation

#### Step 1: Test the hook

Start a new Claude Code session and paste:
```
Analyze this data:
[
  {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
  {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
  {"id": 3, "name": "Carol", "email": "carol@example.com", "role": "user"}
]
```

You'll see a message about compression, then Claude will analyze the compressed data!

#### Step 2: Monitor activity (Optional)

Watch hook activity in real-time:
```bash
# Clear and watch logs
> ~/.claude/tooner_hook.log
tail -f ~/.claude/tooner_hook.log
```

#### Troubleshooting

**"externally-managed-environment" error during installation:**

The automatic installer handles this by trying `pip --user` first. If you're installing manually and see this error:

```bash
# Solution: Use --user flag
pip install --user toon-python

# This installs to your user directory and bypasses the externally-managed restriction
```

**"Could not find a version that satisfies the requirement" error:**

This means your pip package index is outdated. Update pip first:

```bash
# Step 1: Upgrade pip
pip3 install --upgrade pip --user

# Step 2: Install toon-python
pip3 install --user toon-python
```

The automatic installer does this for you.

**Hook not working:**

1. **Check the hook file exists:**
   ```bash
   ls -la ~/.claude/hooks/compress_prompt.py
   ```

2. **Verify toon-python is installed:**
   ```bash
   python3 -c "import toon_python; print('toon-python installed')"
   ```

3. **Test the hook manually:**
   ```bash
   printf '{"prompt": "Analyze: [{\\"id\\": 1, \\"name\\": \\"Alice\\"}, {\\"id\\": 2, \\"name\\": \\"Bob\\"}, {\\"id\\": 3, \\"name\\": \\"Carol\\"}]"}' | ~/.claude/hooks/compress_prompt.py
   ```

   You should see compressed output with token savings.

   **Note:** If nothing is returned, the data doesn't meet compression criteria (needs >30% savings). Try with more fields or more items.

4. **Check the log file:**
   ```bash
   cat ~/.claude/tooner_hook.log
   ```

5. **Verify settings.json syntax:**
   ```bash
   python3 -m json.tool ~/.claude/settings.json
   ```

---

## 🧪 Testing with MCP Server (Optional)

Want to test how Toon compression works before installing the hook? This optional MCP server lets you explore the compression tools interactively using Claude Desktop.

**Note:** This MCP server is for **testing and exploration only**. For automatic compression in Claude Code, use the [hook installation](#-installation) above.

**[← Back to Installation](#-installation)**

### Step 1: Build the Docker image
```bash
git clone https://github.com/mostafamoq/tooner.git
cd tooner
docker build -t tooner-mcp:latest .
```

### Step 2: Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "tooner": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "tooner-mcp:latest"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Restart Claude Desktop to load the MCP server.

### Step 4: Test the tools

Ask Claude:
```
Use the compress_to_toon tool on this data:
[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
```

Claude will have access to 4 tools:
- `compress_to_toon` - Convert JSON to Toon format
- `parse_from_toon` - Convert Toon back to JSON
- `compare_token_usage` - Compare JSON vs Toon tokens
- `should_use_toon` - Analyze if compression is worthwhile

## 📊 Token Savings

Tooner works best with **uniform arrays** (arrays where all objects have the same fields):

| Data Type | Typical Savings | Example |
|-----------|----------------|---------|
| User lists | 40-60% | User profiles, employee data |
| API responses | 35-50% | REST API results, database queries |
| Log entries | 45-65% | Application logs, audit trails |
| Product catalogs | 40-55% | E-commerce items, inventory |

**Minimum requirements for compression:**
- Array with 3+ items
- All objects have the same fields (uniform structure)
- Savings > 30% tokens

**Example:** `[{"id": 1}, {"id": 2}, {"id": 3}]` won't compress (only 25% savings), but `[{"id": 1, "name": "Alice", "email": "alice@example.com"}, ...]` will compress (typically 40-60% savings).

## 🛠️ Development

### Running Tests

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Project Structure

```
tooner/
├── hooks/
│   └── compress_prompt.py      # Main hook - uses toon-python library
├── src/tooner/
│   └── server.py              # MCP test server (optional, for testing)
├── tests/
│   └── test_server.py         # Test suite
├── install.sh                 # Auto-installer (installs toon-python + hook)
├── Dockerfile                 # Docker container (for MCP test server)
├── docker-compose.yml         # Docker Compose config (for testing)
└── pyproject.toml            # Python project metadata
```

## 🔧 How It Works

### Toon Format

Toon is a token-efficient serialization format designed for LLMs:

1. **Declares fields once** (like CSV headers): `data[count]{field1,field2,...}:`
2. **Comma-separated values** (no JSON punctuation)
3. **Automatic quoting** for values containing commas/spaces
4. **Type inference** when parsing back to JSON

**Benefits:**
- Reduces repetitive field names
- Eliminates JSON braces, brackets, quotes
- Maintains full data fidelity
- LLMs can easily understand it

### Hook Behavior

The Claude Code hook:
1. Intercepts your prompt before sending to LLM
2. Detects JSON arrays using regex
3. Analyzes if compression would save >30% tokens
4. Uses the official `toon-python` library to compress uniform arrays
5. Adds compression metadata (original vs compressed tokens)
6. Logs activity to `~/.claude/tooner_hook.log`

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/mostafamoq/tooner.git
cd tooner

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Toon Format](https://github.com/toon-format/toon) - The efficient serialization format
- [toon-python](https://github.com/toon-format/toon-python) - Official Python implementation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Anthropic Claude](https://www.anthropic.com/claude) - AI assistant platform

## 📬 Support

- **Issues:** [GitHub Issues](https://github.com/mostafamoq/tooner/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mostafamoq/tooner/discussions)

## ⭐ Star History

If Tooner saves you tokens and money, please star the repo! ⭐

---

**Made with ❤️ for the Claude community**
