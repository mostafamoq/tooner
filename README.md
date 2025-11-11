# Tooner MCP Server

**Reduce LLM token usage by up to 60% with Toon format compression**

Tooner is a Model Context Protocol (MCP) server that automatically compresses structured JSON data into the efficient [Toon format](https://github.com/toon-format/toon) before sending to LLMs. Perfect for working with large datasets, API responses, and tabular data.

---

**📚 Quick Navigation:** [Installation](#-installation) · [Testing](#-testing-with-claude-desktop) · [How It Works](#-how-it-works) · [Development](#-development) · [Contributing](#-contributing)

---

## ⚡ Get Started

**For Claude Code users:** [Install the hook](#-installation) to automatically compress JSON data and save tokens.

**Want to test first?** [Try it with Claude Desktop](#-testing-with-claude-desktop) to explore the compression tools.

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

### Claude Code Hook (Automatic Compression)

The hook automatically compresses JSON in your prompts **before** they reach the LLM, saving tokens on every request.

**[→ Skip to Testing](#-testing-with-claude-desktop)**

#### Step 1: Copy the hook file
```bash
mkdir -p ~/.claude/hooks
curl -o ~/.claude/hooks/compress_prompt.py \
  https://raw.githubusercontent.com/YOUR_USERNAME/tooner/main/hooks/compress_prompt.py
chmod +x ~/.claude/hooks/compress_prompt.py
```

#### Step 2: Configure Claude Code

Edit or create `~/.claude/settings.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/Users/YOUR_USERNAME/.claude/hooks/compress_prompt.py"
          }
        ]
      }
    ]
  }
}
```

**Replace `/Users/YOUR_USERNAME/` with your actual home path.**

#### Step 3: Test the hook

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

#### Step 4: Monitor activity (Optional)

Watch hook activity in real-time:
```bash
# Clear and watch logs
> ~/.claude/tooner_hook.log
tail -f ~/.claude/tooner_hook.log
```

---

## 🧪 Testing with Claude Desktop

Want to test the Tooner MCP server and its compression tools? Use Claude Desktop with Docker to explore the 4 MCP tools interactively.

**Note:** This is for **testing and exploring** the tools only. For production use with Claude Code, use the [hook installation](#-installation) above.

**[← Back to Installation](#-installation)**

### Step 1: Build the Docker image
```bash
git clone https://github.com/YOUR_USERNAME/tooner.git
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
- All objects have the same fields
- Savings > 10% estimated

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
│   └── compress_prompt.py      # Claude Code hook for automatic compression
├── src/tooner/
│   └── server.py              # MCP server with compression tools
├── tests/
│   └── test_server.py         # Test suite
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Docker Compose config
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
3. Analyzes if compression would save >10% tokens
4. Compresses uniform arrays to Toon format
5. Logs activity to `~/.claude/tooner_hook.log`

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
git clone https://github.com/YOUR_USERNAME/tooner.git
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
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Anthropic Claude](https://www.anthropic.com/claude) - AI assistant platform

## 📬 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/tooner/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/tooner/discussions)

## ⭐ Star History

If Tooner saves you tokens and money, please star the repo! ⭐

---

**Made with ❤️ for the Claude community**
