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
echo -e "${BOLD}Step 2:${RESET} Downloading hook file..."

# Check if we're in the tooner repo or need to download
if [[ -f "hooks/compress_prompt_standalone.py" ]]; then
    # Running from repo directory
    echo -e "${YELLOW}Found local hook file, using it...${RESET}"
    cp "hooks/compress_prompt_standalone.py" "$HOOK_FILE"
else
    # Download from GitHub
    echo -e "Downloading from GitHub..."
    HOOK_URL="https://raw.githubusercontent.com/mostafamoq/tooner/main/hooks/compress_prompt_standalone.py"

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
echo -e "${BOLD}Step 3:${RESET} Setting permissions..."
chmod +x "$HOOK_FILE"
echo -e "${GREEN}✓${RESET} Made hook executable"

echo ""
echo -e "${BOLD}Step 4:${RESET} Configuring Claude Code settings..."

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
echo -e "1. ${BOLD}Test the hook:${RESET}"
echo -e "   Start a new Claude Code session and paste:"
echo -e "   ${YELLOW}Analyze this data:"
echo -e '   [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]'
echo -e "${RESET}"
echo -e "2. ${BOLD}Monitor activity (optional):${RESET}"
echo -e "   ${YELLOW}tail -f ~/.claude/tooner_hook.log${RESET}"
echo ""
echo -e "3. ${BOLD}Uninstall (if needed):${RESET}"
echo -e "   ${YELLOW}rm $HOOK_FILE${RESET}"
echo -e "   Then remove the hook from $SETTINGS_FILE"
echo ""
echo -e "${BOLD}Documentation:${RESET} https://github.com/mostafamoq/tooner"
echo -e "${BOLD}Issues:${RESET} https://github.com/mostafamoq/tooner/issues"
echo ""
echo -e "${GREEN}Happy token saving! 🚀${RESET}"
