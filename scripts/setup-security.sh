#!/bin/bash
# MeKB Security Setup Script
# Sets up secret detection and AI access control

set -e

echo "🔐 MeKB Security Setup"
echo "======================"
echo ""

# Find vault root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$VAULT_ROOT"

echo "Vault: $VAULT_ROOT"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for pre-commit
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    pip3 install pre-commit --user
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Create security config if it doesn't exist
if [ ! -f ".mekb/security.json" ]; then
    echo "📝 Creating security configuration..."
    mkdir -p .mekb
    cat > .mekb/security.json << 'EOF'
{
  "ai_access_control": {
    "enabled": true,
    "mode": "interactive",
    "levels": {
      "public": "allow",
      "personal": "allow",
      "confidential": "ask",
      "secret": "block"
    },
    "write_protection": true,
    "remember_session": true,
    "log_access_attempts": true
  },
  "trusted_ai_providers": {
    "enabled": true,
    "providers": ["bedrock", "local"],
    "trust_level": {
      "bedrock": "confidential",
      "local": "secret",
      "api": "personal",
      "consumer": "personal"
    }
  },
  "folder_inheritance": {
    "enabled": true,
    "folders": {
      "confidential/": "confidential",
      "secret/": "secret",
      "private/": "confidential"
    }
  },
  "secret_detection": {
    "enabled": true,
    "block_commit": true
  }
}
EOF
fi

# Create classified folders
echo "📁 Creating classified folders..."
mkdir -p confidential secret
touch confidential/.gitkeep secret/.gitkeep

# Add to .gitignore if not already there
if ! grep -q "secret/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Classified folders" >> .gitignore
    echo "secret/" >> .gitignore
fi

# Register Claude Code hook
CLAUDE_HOOKS_DIR="$HOME/.claude/hooks"
if [ -d "$HOME/.claude" ]; then
    echo "🔗 Setting up Claude Code hook..."
    mkdir -p "$CLAUDE_HOOKS_DIR"

    # Create hook registration
    HOOK_CONFIG="$HOME/.claude/hooks.json"
    if [ ! -f "$HOOK_CONFIG" ]; then
        echo '{"hooks": []}' > "$HOOK_CONFIG"
    fi

    # Note: Hook registration requires Claude Code restart
    echo "   Hook file: .claude/hooks/classification-guard.py"
    echo "   ⚠️  Add to .claude/settings.json manually (see below)"
fi

# Make scripts executable
chmod +x scripts/*.py scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ Security setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo ""
echo "1. Add the classification hook to .claude/settings.json:"
echo ""
echo '   "hooks": {'
echo '     "PreToolUse": ['
echo '       {'
echo '         "matcher": "Read|Write|Edit|Grep|Glob",'
echo '         "command": "python3 .claude/hooks/classification-guard.py"'
echo '       }'
echo '     ]'
echo '   }'
echo ""
echo "2. Restart Claude Code to load the hook"
echo ""
echo "3. Test with: /classify"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Quick Reference:"
echo "   /classify              - Show classification summary"
echo "   /classify check        - Find files needing classification"
echo "   /classify list secret  - List secret files"
echo "   /classify set FILE confidential - Classify a file"
echo ""
echo "🔐 Classification Levels:"
echo "   public       - AI can access freely"
echo "   personal     - AI can access (default)"
echo "   confidential - AI will ask before access"
echo "   secret       - AI access blocked"
echo ""
