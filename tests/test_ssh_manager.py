"""Unit tests for SSHManager."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ssh_manager import SSHManager


class TestSSHConfigParsing(unittest.TestCase):
    """Test the SSH config block build / replace / remove helpers."""

    def test_build_config_entry(self):
        entry = SSHManager._build_config_entry(
            "github.com-personal", "github.com", "/home/u/.ssh/id_ed25519_personal"
        )
        self.assertIn("Host github.com-personal", entry)
        self.assertIn("HostName github.com", entry)
        self.assertIn("IdentityFile /home/u/.ssh/id_ed25519_personal", entry)
        self.assertIn("IdentitiesOnly yes", entry)

    def test_replace_config_block(self):
        existing = (
            "# mgit-managed: github.com-old\n"
            "Host github.com-old\n"
            "    HostName github.com\n"
            "# end-mgit: github.com-old\n"
            "\n"
            "Host other\n"
            "    HostName other.com\n"
        )
        new_entry = SSHManager._build_config_entry(
            "github.com-old", "github.com", "/new/key"
        )
        result = SSHManager._replace_config_block(existing, "github.com-old", new_entry)
        self.assertIn("/new/key", result)
        self.assertIn("Host other", result)

    def test_remove_config_block(self):
        existing = (
            "# mgit-managed: github.com-work\n"
            "Host github.com-work\n"
            "    HostName github.com\n"
            "# end-mgit: github.com-work\n"
            "\n"
            "Host other\n"
        )
        result = SSHManager._remove_config_block(existing, "github.com-work")
        self.assertNotIn("github.com-work", result)
        self.assertIn("Host other", result)


if __name__ == "__main__":
    unittest.main()