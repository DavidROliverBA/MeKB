#!/usr/bin/env python3
"""
Webhook server for MeKB.
Receive webhooks to create notes, trigger index rebuilds, and run maintenance.

Usage:
    python3 scripts/webhook-server.py                      # Start on port 9876
    python3 scripts/webhook-server.py --port 8888           # Custom port
    python3 scripts/webhook-server.py --token my-secret     # Require auth token

Endpoints:
    POST /api/note           - Create a new note
    POST /api/rebuild-index  - Rebuild search index
    POST /api/rebuild-graph  - Rebuild knowledge graph
    POST /api/health         - Health check
    GET  /api/status         - Server status

Dependencies: Python 3.9+ (stdlib only)
"""

import argparse
import http.server
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def find_vault_root():
    """Find the vault root."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    """Handle incoming webhook requests."""

    # Set by server setup
    vault_root = None
    auth_token = None
    request_count = 0

    def _check_auth(self):
        """Verify auth token if configured."""
        if not self.auth_token:
            return True
        token = self.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            token = self.headers.get("X-Webhook-Token", "")
        return token == self.auth_token

    def _send_json(self, status, data):
        """Send JSON response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        """Read and parse JSON request body."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path

        if path == "/api/status":
            WebhookHandler.request_count += 1
            self._send_json(200, {
                "status": "running",
                "vault": str(self.vault_root),
                "requests_served": WebhookHandler.request_count,
                "uptime_note": "Server started at process launch",
            })
        elif path == "/":
            self._send_json(200, {
                "service": "MeKB Webhook Server",
                "endpoints": {
                    "POST /api/note": "Create a note",
                    "POST /api/rebuild-index": "Rebuild search index",
                    "POST /api/rebuild-graph": "Rebuild knowledge graph",
                    "POST /api/health": "Run health check",
                    "GET /api/status": "Server status",
                },
            })
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests."""
        WebhookHandler.request_count += 1

        if not self._check_auth():
            self._send_json(401, {"error": "Unauthorised"})
            return

        path = urlparse(self.path).path
        data = self._read_body()

        if path == "/api/note":
            self._handle_create_note(data)
        elif path == "/api/rebuild-index":
            self._handle_rebuild_index()
        elif path == "/api/rebuild-graph":
            self._handle_rebuild_graph()
        elif path == "/api/health":
            self._handle_health()
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_create_note(self, data):
        """Create a new note from webhook payload."""
        title = data.get("title")
        if not title:
            self._send_json(400, {"error": "Missing 'title' field"})
            return

        note_type = data.get("type", "Note")
        content = data.get("content", "")
        tags = data.get("tags", [])
        classification = data.get("classification", "personal")

        # Validate classification
        if classification in ("secret", "confidential"):
            self._send_json(403, {"error": "Cannot create secret/confidential notes via webhook"})
            return

        # Sanitise title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', "", title)
        filename = f"{note_type} - {safe_title}.md"
        filepath = self.vault_root / filename

        if filepath.exists():
            self._send_json(409, {"error": f"Note already exists: {filename}"})
            return

        # Build frontmatter
        today = datetime.now().strftime("%Y-%m-%d")
        tags_yaml = ", ".join(tags) if tags else ""

        note_content = f"""---
type: {note_type}
title: {title}
created: {today}
tags: [{tags_yaml}]
classification: {classification}
---

# {title}

{content}
"""
        filepath.write_text(note_content)

        self._send_json(201, {
            "created": filename,
            "path": str(filepath.relative_to(self.vault_root)),
        })

    def _handle_rebuild_index(self):
        """Trigger search index rebuild."""
        script = self.vault_root / "scripts" / "build-index.py"
        if not script.exists():
            self._send_json(500, {"error": "build-index.py not found"})
            return

        try:
            result = subprocess.run(
                [sys.executable, str(script), "--stats"],
                capture_output=True, text=True, timeout=30,
                cwd=str(self.vault_root),
            )
            self._send_json(200, {
                "action": "rebuild-index",
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
            })
        except subprocess.TimeoutExpired:
            self._send_json(500, {"error": "Index rebuild timed out"})

    def _handle_rebuild_graph(self):
        """Trigger graph rebuild."""
        script = self.vault_root / "scripts" / "build-graph.py"
        if not script.exists():
            self._send_json(500, {"error": "build-graph.py not found"})
            return

        try:
            result = subprocess.run(
                [sys.executable, str(script), "--stats"],
                capture_output=True, text=True, timeout=30,
                cwd=str(self.vault_root),
            )
            self._send_json(200, {
                "action": "rebuild-graph",
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
            })
        except subprocess.TimeoutExpired:
            self._send_json(500, {"error": "Graph rebuild timed out"})

    def _handle_health(self):
        """Run vault health check."""
        vault = self.vault_root
        note_count = len(list(vault.rglob("*.md")))
        has_index = (vault / ".mekb" / "search.db").exists()
        has_graph = (vault / ".mekb" / "graph.json").exists()
        has_embeddings = (vault / ".mekb" / "embeddings.json").exists()

        self._send_json(200, {
            "vault": str(vault),
            "notes": note_count,
            "indexes": {
                "search": has_index,
                "graph": has_graph,
                "embeddings": has_embeddings,
            },
        })

    def log_message(self, format, *args):
        """Custom log format."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {args[0]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="MeKB webhook server")
    parser.add_argument("--port", "-p", type=int, default=9876,
                       help="Server port (default: 9876)")
    parser.add_argument("--token", "-t",
                       help="Auth token (also reads MEKB_WEBHOOK_TOKEN env var)")
    parser.add_argument("--vault", help="Vault root directory")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    auth_token = args.token or os.environ.get("MEKB_WEBHOOK_TOKEN")

    WebhookHandler.vault_root = vault_root
    WebhookHandler.auth_token = auth_token

    server = http.server.HTTPServer(("127.0.0.1", args.port), WebhookHandler)

    print(f"MeKB Webhook Server")
    print(f"  Vault:  {vault_root}")
    print(f"  Listen: http://127.0.0.1:{args.port}")
    print(f"  Auth:   {'enabled' if auth_token else 'disabled (use --token)'}")
    print()
    print("Endpoints:")
    print("  POST /api/note           Create a note")
    print("  POST /api/rebuild-index  Rebuild search index")
    print("  POST /api/rebuild-graph  Rebuild knowledge graph")
    print("  POST /api/health         Health check")
    print("  GET  /api/status         Server status")
    print()
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
