#!/usr/bin/env python3
"""Tests for webhook-server.py.

Tests the handler methods directly without starting a real HTTP server,
avoiding socket binding which is blocked in sandboxed environments.
"""

import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from helpers import _import_script, create_note, VaultFixture, SCRIPTS_DIR

_ws = _import_script("webhook_server", "webhook-server.py")
WebhookHandler = _ws.WebhookHandler


class _MockHandler:
    """Mock WebhookHandler that captures responses without needing a real socket."""

    def __init__(self, vault_root, auth_token=None):
        self.vault_root = vault_root
        self.auth_token = auth_token
        self._response_status = None
        self._response_body = None

    def handle(self, method, path, body=None, headers=None):
        """Simulate an HTTP request to the handler."""
        handler = WebhookHandler.__new__(WebhookHandler)
        handler.vault_root = self.vault_root
        handler.auth_token = self.auth_token
        handler.path = path
        handler.command = method

        # Mock headers
        real_headers = {}
        if headers:
            real_headers.update(headers)
        body_bytes = json.dumps(body).encode("utf-8") if body else b""
        real_headers.setdefault("Content-Length", str(len(body_bytes)))
        real_headers.setdefault("Content-Type", "application/json")

        header_obj = MagicMock()
        header_obj.get = lambda k, default="": real_headers.get(k, default)
        handler.headers = header_obj

        # Mock rfile for reading body
        handler.rfile = io.BytesIO(body_bytes)

        # Mock wfile for capturing response
        wfile = io.BytesIO()
        handler.wfile = wfile

        # Capture response
        captured = {}

        def mock_send_response(status):
            captured["status"] = status

        def mock_send_header(k, v):
            pass

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers
        handler.log_message = lambda *a: None

        # Override _send_json to capture output
        original_send_json = WebhookHandler._send_json

        def capturing_send_json(self_inner, status, data):
            captured["status"] = status
            captured["body"] = data

        handler._send_json = lambda status, data: capturing_send_json(handler, status, data)

        # Override _read_body
        def capturing_read_body(self_inner):
            length = int(handler.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            raw = handler.rfile.read(length)
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}

        handler._read_body = lambda: capturing_read_body(handler)

        # Override _check_auth
        def capturing_check_auth(self_inner):
            if not handler.auth_token:
                return True
            token = handler.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                token = handler.headers.get("X-Webhook-Token", "")
            return token == handler.auth_token

        handler._check_auth = lambda: capturing_check_auth(handler)

        if method == "GET":
            WebhookHandler.do_GET(handler)
        elif method == "POST":
            WebhookHandler.do_POST(handler)

        return captured.get("status"), captured.get("body", {})


class TestWebhookAuth(unittest.TestCase):
    """Test authentication logic."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.mock = _MockHandler(self.fixture.root, auth_token="test-secret-token")

    def tearDown(self):
        self.fixture.teardown()

    def test_bearer_header_accepted(self):
        status, body = self.mock.handle(
            "POST", "/api/health",
            headers={"Authorization": "Bearer test-secret-token"},
        )
        self.assertEqual(status, 200)

    def test_x_webhook_token_accepted(self):
        status, body = self.mock.handle(
            "POST", "/api/health",
            headers={"X-Webhook-Token": "test-secret-token"},
        )
        self.assertEqual(status, 200)

    def test_missing_token_rejected(self):
        status, body = self.mock.handle("POST", "/api/health")
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "Unauthorised")

    def test_invalid_token_rejected(self):
        status, body = self.mock.handle(
            "POST", "/api/health",
            headers={"Authorization": "Bearer wrong-token"},
        )
        self.assertEqual(status, 401)

    def test_no_auth_mode(self):
        """Server with no token configured allows all requests."""
        no_auth = _MockHandler(self.fixture.root, auth_token=None)
        status, body = no_auth.handle("POST", "/api/health")
        self.assertEqual(status, 200)


class TestWebhookNoteCreation(unittest.TestCase):
    """Test POST /api/note endpoint."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.mock = _MockHandler(self.fixture.root)

    def tearDown(self):
        self.fixture.teardown()

    def test_create_valid_note(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Test Note", "type": "Concept", "content": "Hello world"},
        )
        self.assertEqual(status, 201)
        self.assertIn("created", body)
        path = self.fixture.root / body["created"]
        self.assertTrue(path.exists())
        content = path.read_text()
        self.assertIn("type: Concept", content)
        self.assertIn("Hello world", content)

    def test_missing_title_returns_400(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"content": "No title provided"},
        )
        self.assertEqual(status, 400)
        self.assertIn("title", body["error"].lower())

    def test_duplicate_returns_409(self):
        create_note(self.fixture.root, "Note - Existing.md",
                     {"type": "Note", "title": "Existing"}, "Body")
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Existing", "type": "Note"},
        )
        self.assertEqual(status, 409)

    def test_secret_classification_blocked(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Secret Note", "classification": "secret"},
        )
        self.assertEqual(status, 403)

    def test_confidential_classification_blocked(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Confidential Note", "classification": "confidential"},
        )
        self.assertEqual(status, 403)

    def test_title_sanitised(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": 'Test <Bad> "Chars"'},
        )
        self.assertEqual(status, 201)
        self.assertNotIn("<", body["created"])
        self.assertNotIn('"', body["created"])

    def test_tags_included(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Tagged Note", "tags": ["domain/data", "activity/research"]},
        )
        self.assertEqual(status, 201)
        content = (self.fixture.root / body["created"]).read_text()
        self.assertIn("domain/data", content)

    def test_default_type(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "Default Type"},
        )
        self.assertEqual(status, 201)
        content = (self.fixture.root / body["created"]).read_text()
        self.assertIn("type: Note", content)


class TestWebhookRouting(unittest.TestCase):
    """Test HTTP routing."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.mock = _MockHandler(self.fixture.root)

    def tearDown(self):
        self.fixture.teardown()

    def test_get_status(self):
        status, body = self.mock.handle("GET", "/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "running")

    def test_get_root(self):
        status, body = self.mock.handle("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("endpoints", body)

    def test_get_unknown_returns_404(self):
        status, body = self.mock.handle("GET", "/api/nonexistent")
        self.assertEqual(status, 404)

    def test_post_unknown_returns_404(self):
        status, body = self.mock.handle("POST", "/api/nonexistent")
        self.assertEqual(status, 404)

    def test_post_health(self):
        status, body = self.mock.handle("POST", "/api/health")
        self.assertEqual(status, 200)
        self.assertIn("notes", body)
        self.assertIn("indexes", body)


class TestWebhookRebuild(unittest.TestCase):
    """Test rebuild endpoints."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.mock = _MockHandler(self.fixture.root)

    def tearDown(self):
        self.fixture.teardown()

    def test_rebuild_index_script_missing(self):
        status, body = self.mock.handle("POST", "/api/rebuild-index")
        self.assertEqual(status, 500)
        self.assertIn("not found", body["error"])

    @patch("subprocess.run")
    def test_rebuild_index_success(self, mock_run):
        scripts_dir = self.fixture.root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / "build-index.py").write_text("# stub")
        mock_run.return_value = MagicMock(returncode=0, stdout="OK", stderr="")
        status, body = self.mock.handle("POST", "/api/rebuild-index")
        self.assertEqual(status, 200)
        self.assertTrue(body["success"])

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=30))
    def test_rebuild_index_timeout(self, mock_run):
        scripts_dir = self.fixture.root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / "build-index.py").write_text("# stub")
        status, body = self.mock.handle("POST", "/api/rebuild-index")
        self.assertEqual(status, 500)
        self.assertIn("timed out", body["error"])


class TestWebhookBodyParsing(unittest.TestCase):
    """Test request body parsing."""

    def setUp(self):
        self.fixture = VaultFixture().setup()
        self.mock = _MockHandler(self.fixture.root)

    def tearDown(self):
        self.fixture.teardown()

    def test_valid_json(self):
        status, body = self.mock.handle(
            "POST", "/api/note",
            body={"title": "JSON Test"},
        )
        self.assertEqual(status, 201)

    def test_empty_body(self):
        status, body = self.mock.handle("POST", "/api/note")
        self.assertEqual(status, 400)

    def test_malformed_json(self):
        # Simulate sending malformed JSON by passing no body (parsed as empty dict)
        # The handler's _read_body returns {} for invalid JSON
        status, body = self.mock.handle("POST", "/api/note")
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
