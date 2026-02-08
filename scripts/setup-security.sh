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

# ── Encryption Setup (optional) ─────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 Encryption Setup (optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "MeKB can encrypt notes classified as confidential or secret"
echo "using age (actually good encryption). This is optional."
echo ""

read -p "Set up encryption? (y/N) " SETUP_ENCRYPT
if [[ "$SETUP_ENCRYPT" =~ ^[Yy]$ ]]; then

    # Check/install age
    if ! command -v age &> /dev/null; then
        echo ""
        echo "📦 age is required for encryption."
        if command -v brew &> /dev/null; then
            read -p "Install age via Homebrew? (y/N) " INSTALL_AGE
            if [[ "$INSTALL_AGE" =~ ^[Yy]$ ]]; then
                brew install age
            else
                echo "Install manually: https://github.com/FiloSottile/age#installation"
                echo "Skipping encryption setup."
                SETUP_ENCRYPT="n"
            fi
        else
            echo "Install age manually: https://github.com/FiloSottile/age#installation"
            echo "Then re-run this script."
            SETUP_ENCRYPT="n"
        fi
    fi
fi

if [[ "$SETUP_ENCRYPT" =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔑 Generating encryption keys..."
    echo ""

    mkdir -p .mekb

    # Generate primary age key
    if [ ! -f ".mekb/age-key.txt" ]; then
        age-keygen -o .mekb/age-key.txt 2>/tmp/mekb-keygen-output.txt
        PRIMARY_PUBKEY=$(grep "public key:" /tmp/mekb-keygen-output.txt | awk '{print $NF}')
        rm -f /tmp/mekb-keygen-output.txt
        echo "   ✅ Primary key generated"
        echo "   Public key: $PRIMARY_PUBKEY"
    else
        PRIMARY_PUBKEY=$(grep "public key:" .mekb/age-key.txt | awk '{print $NF}')
        echo "   ✅ Primary key already exists"
        echo "   Public key: $PRIMARY_PUBKEY"
    fi

    # Generate backup passphrase key
    if [ ! -f ".mekb/backup-key.txt" ]; then
        age-keygen -o .mekb/backup-key.txt 2>/tmp/mekb-keygen-output.txt
        BACKUP_PUBKEY=$(grep "public key:" /tmp/mekb-keygen-output.txt | awk '{print $NF}')
        rm -f /tmp/mekb-keygen-output.txt
        echo "   ✅ Backup key generated"
        echo "   Public key: $BACKUP_PUBKEY"
    else
        BACKUP_PUBKEY=$(grep "public key:" .mekb/backup-key.txt | awk '{print $NF}')
        echo "   ✅ Backup key already exists"
        echo "   Public key: $BACKUP_PUBKEY"
    fi

    # Update security.json with recipient keys
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
from pathlib import Path

config_path = Path('.mekb/security.json')
config = json.loads(config_path.read_text()) if config_path.exists() else {}

config.setdefault('encryption', {})
config['encryption']['enabled'] = True
config['encryption']['tool'] = 'age'
config['encryption']['levels_to_encrypt'] = ['secret', 'confidential']
config['encryption']['format'] = 'split'
config['encryption']['recipients'] = ['$PRIMARY_PUBKEY', '$BACKUP_PUBKEY']
config['encryption']['primary_identity'] = '.mekb/age-key.txt'
config['encryption']['backup_identity'] = '.mekb/backup-key.txt'
config['encryption']['session_timeout_minutes'] = 30
config['encryption']['index_encrypted_body'] = False
config['encryption']['encrypt_on_classify'] = True

config_path.write_text(json.dumps(config, indent=2) + '\n')
print('   ✅ Encryption config saved to .mekb/security.json')
"
    fi

    # Ensure key files are gitignored
    for KEYFILE in ".mekb/age-key.txt" ".mekb/backup-key.txt"; do
        if ! grep -q "$KEYFILE" .gitignore 2>/dev/null; then
            echo "" >> .gitignore
            echo "# Encryption key - NEVER commit" >> .gitignore
            echo "$KEYFILE" >> .gitignore
        fi
    done
    echo "   ✅ Key files added to .gitignore"

    echo ""
    echo "⚠️  IMPORTANT: Back up your keys!"
    echo "   Store .mekb/backup-key.txt in your password manager (e.g. Bitwarden)"
    echo "   If you lose both keys, encrypted notes CANNOT be recovered."
    echo ""
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
if [[ "$SETUP_ENCRYPT" =~ ^[Yy]$ ]]; then
echo "🔑 Encryption Commands:"
echo "   /encrypt <file>        - Encrypt a note"
echo "   /decrypt <file>        - Decrypt a note"
echo "   /encrypt audit         - Check encryption status"
echo "   /encrypt setup         - Re-run encryption setup"
echo ""
fi
