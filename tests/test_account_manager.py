"""Unit tests for AccountManager."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

# Ensure src/ is importable
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from account_manager import AccountManager, Account


class TestAccount(unittest.TestCase):
    def test_to_dict_and_from_dict(self):
        acct = Account(
            name="personal",
            git_username="john",
            git_email="john@example.com",
            provider="github",
            host_alias="github.com-personal",
            ssh_key_path="/home/john/.ssh/id_ed25519_personal",
        )
        d = acct.to_dict()
        restored = Account.from_dict(d)
        self.assertEqual(restored.name, "personal")
        self.assertEqual(restored.git_email, "john@example.com")
        self.assertFalse(restored.is_default)


class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_file = Path(self.tmpdir) / "config.yaml"

    def _make_manager(self):
        with patch("account_manager.get_mgit_config_file", return_value=self.config_file):
            return AccountManager()

    def test_add_account(self):
        mgr = self._make_manager()
        acct = mgr.add_account(
            name="work",
            git_username="jdoe",
            git_email="jdoe@corp.com",
            provider="github",
            host_alias="github.com-work",
            ssh_key_path="/tmp/key",
        )
        self.assertEqual(acct.name, "work")
        self.assertTrue(acct.is_default)  # first account → default

    def test_add_duplicate_raises(self):
        mgr = self._make_manager()
        mgr.add_account(
            name="work",
            git_username="jdoe",
            git_email="jdoe@corp.com",
            provider="github",
            host_alias="github.com-work",
            ssh_key_path="/tmp/key",
        )
        with self.assertRaises(ValueError):
            mgr.add_account(
                name="work",
                git_username="jdoe2",
                git_email="jdoe2@corp.com",
                provider="github",
                host_alias="github.com-work2",
                ssh_key_path="/tmp/key2",
            )

    def test_invalid_email_raises(self):
        mgr = self._make_manager()
        with self.assertRaises(ValueError):
            mgr.add_account(
                name="bad",
                git_username="x",
                git_email="not-an-email",
                provider="github",
                host_alias="h",
                ssh_key_path="/tmp/k",
            )

    def test_remove_account(self):
        mgr = self._make_manager()
        mgr.add_account(
            name="tmp",
            git_username="u",
            git_email="u@e.com",
            provider="github",
            host_alias="h",
            ssh_key_path="/tmp/k",
        )
        mgr.remove_account("tmp")
        self.assertIsNone(mgr.get_account("tmp"))

    def test_set_default(self):
        mgr = self._make_manager()
        mgr.add_account(
            name="a", git_username="a", git_email="a@e.com",
            provider="github", host_alias="h1", ssh_key_path="/tmp/k1",
        )
        mgr.add_account(
            name="b", git_username="b", git_email="b@e.com",
            provider="github", host_alias="h2", ssh_key_path="/tmp/k2",
        )
        mgr.set_default("b")
        self.assertTrue(mgr.get_account("b").is_default)
        self.assertFalse(mgr.get_account("a").is_default)


if __name__ == "__main__":
    unittest.main()