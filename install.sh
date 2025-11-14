#!/bin/bash
# Tooner Installation Script
# Automatically installs the Tooner hook for Claude Code

set -e  # Exit on error

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Tooner - Claude Code Hook Installer${RESET}"
echo -e "${BOLD}  Reduce LLM token usage by up to 60% with automatic JSON compression${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Detect OS
OS="$(uname)"
if [[ "$OS" == "Darwin" ]]; then
    CLAUDE_DIR="$HOME/.claude"
elif [[ "$OS" == "Linux" ]]; then
    CLAUDE_DIR="$HOME/.claude"
elif [[ "$OS" =~ "MINGW" ]] || [[ "$OS" =~ "MSYS" ]]; then
    CLAUDE_DIR="$HOME/.claude"
else
    echo -e "${RED}Unsupported OS: $OS${RESET}"
    exit 1
fi

HOOKS_DIR="$CLAUDE_DIR/hooks"
HOOK_FILE="$HOOKS_DIR/compress_prompt.py"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

echo -e "${BOLD}Step 1:${RESET} Creating directories..."
mkdir -p "$HOOKS_DIR"
echo -e "${GREEN}✓${RESET} Created $HOOKS_DIR"

echo ""
echo -e "${BOLD}Step 2:${RESET} Installing toon-python library..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "Detected Python ${PYTHON_VERSION}"

# toon-python requires Python 3.10+
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${YELLOW}⚠ Python ${PYTHON_VERSION} detected, but toon-python requires Python 3.10+${RESET}"
    echo -e "${YELLOW}⚠ Hook will be installed but compression will be disabled${RESET}"
    echo -e ""
    echo -e "${BOLD}To enable compression, upgrade Python:${RESET}"
    echo -e "  ${YELLOW}brew install python@3.13${RESET}  # macOS"
    echo -e "  ${YELLOW}sudo apt install python3.13${RESET}  # Ubuntu/Debian"
    echo -e ""
    # Continue installation without toon-python
else
    # Find pip command
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        echo -e "${RED}Error: pip is required but not found${RESET}"
        exit 1
    fi

    # Upgrade pip first to ensure package index is up to date
    echo -e "Updating pip..."
    $PIP_CMD install --upgrade pip --user -q 2>/dev/null || true

    # Try different installation methods
    echo -e "Installing official toon-python library..."

    # Try 1: User install (works on externally-managed environments)
    if $PIP_CMD install --user -q toon-python 2>/dev/null; then
        echo -e "${GREEN}✓${RESET} toon-python library installed (user mode)"
    # Try 2: Standard install
    elif $PIP_CMD install -q toon-python 2>/dev/null; then
        echo -e "${GREEN}✓${RESET} toon-python library installed"
    # Try 3: Break system packages (for stubborn externally-managed environments)
    elif $PIP_CMD install --break-system-packages -q toon-python 2>/dev/null; then
        echo -e "${GREEN}✓${RESET} toon-python library installed (system packages)"
    else
        echo -e "${YELLOW}⚠ Failed to install toon-python${RESET}"
        echo -e "${YELLOW}⚠ Hook will be installed but compression will be disabled${RESET}"
        echo -e ""
        echo -e "${BOLD}Try manually:${RESET}"
        echo -e "  ${YELLOW}pip3 install --upgrade pip --user${RESET}"
        echo -e "  ${YELLOW}pip3 install --user toon-python${RESET}"
        echo -e ""
    fi
fi

echo ""
echo -e "${BOLD}Step 3:${RESET} Downloading hook file..."

# Check if we're in the tooner repo or need to download
if [[ -f "hooks/compress_prompt.py" ]]; then
    # Running from repo directory
    echo -e "${YELLOW}Found local hook file, using it...${RESET}"
    cp "hooks/compress_prompt.py" "$HOOK_FILE"
else
    # Download from GitHub
    echo -e "Downloading from GitHub..."
    HOOK_URL="https://raw.githubusercontent.com/mostafamoq/tooner/main/hooks/compress_prompt.py"

    if command -v curl &> /dev/null; then
        curl -fsSL "$HOOK_URL" -o "$HOOK_FILE"
    elif command -v wget &> /dev/null; then
        wget -q "$HOOK_URL" -O "$HOOK_FILE"
    else
        echo -e "${RED}Error: curl or wget is required to download the hook${RESET}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${RESET} Hook file installed to $HOOK_FILE"

echo ""
echo -e "${BOLD}Step 4:${RESET} Setting permissions..."
chmod +x "$HOOK_FILE"
echo -e "${GREEN}✓${RESET} Made hook executable"

echo ""
echo -e "${BOLD}Step 5:${RESET} Configuring Claude Code settings..."

# Check if settings.json exists
if [[ -f "$SETTINGS_FILE" ]]; then
    echo -e "${YELLOW}Found existing settings.json${RESET}"

    # Backup existing settings
    BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✓${RESET} Backed up to $BACKUP_FILE"

    # Check if hook already configured
    if grep -q "compress_prompt.py" "$SETTINGS_FILE"; then
        echo -e "${YELLOW}Hook already configured in settings.json${RESET}"
    else
        echo -e "${YELLOW}Adding hook to existing settings...${RESET}"

        # Use Python to merge the hook config
        python3 << 'EOF'
import json
import sys

settings_file = sys.argv[1]
hook_file = sys.argv[2]

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

# Add hook configuration
if 'hooks' not in settings:
    settings['hooks'] = {}

if 'UserPromptSubmit' not in settings['hooks']:
    settings['hooks']['UserPromptSubmit'] = []

# Add our hook if not already present
hook_config = {
    "hooks": [
        {
            "type": "command",
            "command": hook_file
        }
    ]
}

# Check if already exists
exists = any(
    h.get('hooks', [{}])[0].get('command', '').endswith('compress_prompt.py')
    for h in settings['hooks']['UserPromptSubmit']
)

if not exists:
    settings['hooks']['UserPromptSubmit'].append(hook_config)

# Write back
with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print("✓ Updated settings.json")
EOF
        python3 -c "import sys; sys.exit(0)" "$SETTINGS_FILE" "$HOOK_FILE" || {
            echo -e "${RED}Error: Failed to update settings.json${RESET}"
            echo -e "${YELLOW}Please manually add the hook configuration.${RESET}"
            exit 1
        }
    fi
else
    echo -e "${YELLOW}Creating new settings.json${RESET}"

    # Create new settings.json
    cat > "$SETTINGS_FILE" << EOF
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOOK_FILE"
          }
        ]
      }
    ]
  }
}
EOF
    echo -e "${GREEN}✓${RESET} Created $SETTINGS_FILE"
fi

echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}${BOLD}✓ Installation Complete!${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "${BOLD}Next Steps:${RESET}"
echo ""
echo -e "1. ${BOLD}Test the hook manually (optional):${RESET}"
echo -e "   ${YELLOW}printf '{\"prompt\": \"Analyze: [{\\\\\"id\\\\\": 1, \\\\\"name\\\\\": \\\\\"Alice\\\\\"}, {\\\\\"id\\\\\": 2, \\\\\"name\\\\\": \\\\\"Bob\\\\\"}, {\\\\\"id\\\\\": 3, \\\\\"name\\\\\": \\\\\"Carol\\\\\"}]\"}' | ~/.claude/hooks/compress_prompt.py${RESET}"
echo -e ""
echo -e "2. ${BOLD}Test in Claude Code:${RESET}"
echo -e "   Start a new Claude Code session and paste:"
echo -e "   ${YELLOW}Analyze this data:"
echo -e '   [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Carol"}]'
echo -e "${RESET}"
echo -e "3. ${BOLD}Monitor activity (optional):${RESET}"
echo -e "   ${YELLOW}tail -f ~/.claude/tooner_hook.log${RESET}"
echo ""
echo -e "4. ${BOLD}Uninstall (if needed):${RESET}"
echo -e "   ${YELLOW}rm $HOOK_FILE${RESET}"
echo -e "   Then remove the hook from $SETTINGS_FILE"
echo ""
echo -e "${BOLD}Documentation:${RESET} https://github.com/mostafamoq/tooner"
echo -e "${BOLD}Issues:${RESET} https://github.com/mostafamoq/tooner/issues"
echo ""
echo -e "${GREEN}Happy token saving! 🚀${RESET}"
