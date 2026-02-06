#!/usr/bin/env python3
"""Tests for notify.py."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from helpers import _import_script, VaultFixture, SCRIPTS_DIR

_nt = _import_script("notify", "notify.py")
load_config = _nt.load_config
detect_backends = _nt.detect_backends
send_desktop = _nt.send_desktop
send_slack = _nt.send_slack
send_discord = _nt.send_discord
send_email = _nt.send_email
send_notification = _nt.send_notification


class TestLoadConfig(unittest.TestCase):
    """Test YAML config loading."""

    def setUp(self):
        self.fixture = VaultFixture().setup()

    def tearDown(self):
        self.fixture.teardown()

    def test_valid_config(self):
        config_path = self.fixture.root / ".mekb" / "notifications.yaml"
        config_path.write_text(
            "slack:\n  webhook_url: https://hooks.slack.com/test\n"
            "discord:\n  webhook_url: https://discord.com/api/webhooks/test\n"
        )
        config = load_config(self.fixture.root)
        self.assertEqual(config["slack"]["webhook_url"], "https://hooks.slack.com/test")
        self.assertEqual(config["discord"]["webhook_url"], "https://discord.com/api/webhooks/test")

    def test_empty_file(self):
        config_path = self.fixture.root / ".mekb" / "notifications.yaml"
        config_path.write_text("")
        config = load_config(self.fixture.root)
        self.assertEqual(config, {})

    def test_boolean_values(self):
        config_path = self.fixture.root / ".mekb" / "notifications.yaml"
        config_path.write_text("desktop:\n  sound: true\n  enabled: false\n")
        config = load_config(self.fixture.root)
        self.assertIs(config["desktop"]["sound"], True)
        self.assertIs(config["desktop"]["enabled"], False)

    def test_null_values(self):
        config_path = self.fixture.root / ".mekb" / "notifications.yaml"
        config_path.write_text("slack:\n  webhook_url: null\n")
        config = load_config(self.fixture.root)
        self.assertIsNone(config["slack"]["webhook_url"])

    def test_missing_file(self):
        config = load_config(self.fixture.root)
        self.assertEqual(config, {})


class TestDetectBackends(unittest.TestCase):
    """Test backend detection logic."""

    @patch("platform.system", return_value="Darwin")
    def test_desktop_on_darwin(self, mock_sys):
        available = detect_backends({})
        self.assertIn("desktop", available)

    @patch("platform.system", return_value="Linux")
    def test_desktop_absent_on_linux(self, mock_sys):
        available = detect_backends({})
        self.assertNotIn("desktop", available)

    @patch("platform.system", return_value="Linux")
    def test_slack_with_webhook(self, mock_sys):
        config = {"slack": {"webhook_url": "https://hooks.slack.com/test"}}
        available = detect_backends(config)
        self.assertIn("slack", available)

    @patch("platform.system", return_value="Linux")
    def test_discord_with_webhook(self, mock_sys):
        config = {"discord": {"webhook_url": "https://discord.com/api/webhooks/test"}}
        available = detect_backends(config)
        self.assertIn("discord", available)

    @patch("platform.system", return_value="Linux")
    def test_email_with_to_address(self, mock_sys):
        config = {"email": {"to": "user@example.com"}}
        available = detect_backends(config)
        self.assertIn("email", available)


class TestSendDesktop(unittest.TestCase):
    """Test macOS desktop notification sending."""

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.run")
    def test_calls_osascript(self, mock_run, mock_sys):
        mock_run.return_value = MagicMock(returncode=0)
        result = send_desktop("Test Title", "Test Message")
        self.assertTrue(result)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "osascript")

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.run")
    def test_escapes_quotes(self, mock_run, mock_sys):
        mock_run.return_value = MagicMock(returncode=0)
        send_desktop('Title "with" quotes', 'Message "here"')
        script_arg = mock_run.call_args[0][0][2]
        self.assertNotIn('"with"', script_arg)
        self.assertIn('\\"with\\"', script_arg)

    @patch("platform.system", return_value="Linux")
    def test_raises_on_non_darwin(self, mock_sys):
        with self.assertRaises(RuntimeError):
            send_desktop("Test", "Message")


class TestSendSlack(unittest.TestCase):
    """Test Slack webhook sending."""

    @patch("urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = send_slack("Title", "Message", "https://hooks.slack.com/test")
        self.assertTrue(result)
        # Verify payload format
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data)
        self.assertIn("*Title*", payload["text"])

    def test_no_webhook_raises(self):
        with self.assertRaises(ValueError):
            send_slack("Title", "Message", None)

    @patch("urllib.request.urlopen")
    def test_payload_format(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        send_slack("Alert", "Something happened", "https://hooks.slack.com/x")
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data)
        self.assertEqual(payload["text"], "*Alert*\nSomething happened")


class TestSendDiscord(unittest.TestCase):
    """Test Discord webhook sending."""

    @patch("urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = send_discord("Title", "Message", "https://discord.com/api/webhooks/test")
        self.assertTrue(result)

    def test_no_webhook_raises(self):
        with self.assertRaises(ValueError):
            send_discord("Title", "Message", None)


class TestSendEmail(unittest.TestCase):
    """Test email sending via SMTP."""

    @patch("smtplib.SMTP")
    def test_success(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = lambda s: mock_smtp
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        config = {"smtp_host": "localhost", "smtp_port": "25", "to": "user@example.com"}
        result = send_email("Test", "Message", config)
        self.assertTrue(result)
        mock_smtp.send_message.assert_called_once()

    def test_no_to_address_raises(self):
        with self.assertRaises(ValueError):
            send_email("Test", "Message", {})

    @patch("smtplib.SMTP")
    def test_starttls_on_port_587(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__ = lambda s: mock_smtp
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        config = {"smtp_host": "smtp.example.com", "smtp_port": "587",
                  "to": "user@example.com"}
        send_email("Test", "Message", config)
        mock_smtp.starttls.assert_called_once()


class TestSendNotification(unittest.TestCase):
    """Test notification dispatch."""

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.run")
    def test_auto_detect_first_backend(self, mock_run, mock_sys):
        mock_run.return_value = MagicMock(returncode=0)
        result = send_notification("Test", "Message", config={})
        self.assertTrue(result)

    @patch("urllib.request.urlopen")
    def test_specific_backend(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        config = {"slack": {"webhook_url": "https://hooks.slack.com/test"}}
        result = send_notification("Test", "Message", backend="slack", config=config)
        self.assertTrue(result)

    @patch("platform.system", return_value="Linux")
    def test_no_backends_returns_false(self, mock_sys):
        result = send_notification("Test", "Message", config={})
        self.assertFalse(result)

    def test_unknown_backend_returns_false(self):
        result = send_notification("Test", "Message", backend="carrier_pigeon", config={})
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
