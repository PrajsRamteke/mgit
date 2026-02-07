"""
SSH key generation and SSH config management for multiple Git accounts.
"""

import os
from pathlib import Path
from typing import Optional

from utils import (
    get_ssh_dir,
    get_ssh_config_file,
    run_command,
    print_success,
    print_error,
    print_info,
    print_warning,
    console,
)


# ---------- Supported hosting providers ----------

PROVIDER_HOSTS = {
    "github": "github.com",
    "gitlab": "gitlab.com",
    "bitbucket": "bitbucket.org",
    "custom": None,
}


class SSHManager:
    """Manage SSH keys and SSH config entries for multiple Git accounts."""

    def __init__(self):
        self.ssh_dir = get_ssh_dir()
        self.ssh_config_file = get_ssh_config_file()

    # ---- Key generation ----

    def generate_ssh_key(
        self,
        account_name: str,
        email: str,
        key_type: str = "ed25519",
        passphrase: str = "",
    ) -> tuple[Path, Path]:
        """
        Generate a new SSH key pair for the given account.

        Returns (private_key_path, public_key_path).
        """
        key_filename = f"id_{key_type}_{account_name}"
        private_key_path = self.ssh_dir / key_filename
        public_key_path = self.ssh_dir / f"{key_filename}.pub"

        if private_key_path.exists():
            print_warning(
                f"SSH key already exists for account '{account_name}'. Skipping generation."
            )
            return private_key_path, public_key_path

        cmd = [
            "ssh-keygen",
            "-t", key_type,
            "-C", email,
            "-f", str(private_key_path),
            "-N", passphrase,
        ]

        # ed25519 doesn't use -b, rsa does
        if key_type == "rsa":
            cmd.extend(["-b", "4096"])

        run_command(cmd)
        print_success(f"SSH key generated: {private_key_path}")
        return private_key_path, public_key_path

    # ---- SSH config helpers ----

    def add_ssh_config_entry(
        self,
        account_name: str,
        provider: str,
        custom_host: Optional[str] = None,
    ) -> str:
        """
        Add (or update) an SSH config entry for the account.

        Returns the Host alias used in ~/.ssh/config.
        """
        if provider == "custom" and custom_host is None:
            raise ValueError("custom_host is required when provider is 'custom'")

        actual_host = PROVIDER_HOSTS.get(provider, custom_host)
        host_alias = f"{actual_host}-{account_name}"

        key_path = self._find_key_for_account(account_name)
        if key_path is None:
            print_error(
                f"No SSH key found for account '{account_name}'. "
                "Generate one first with `mgit add`."
            )
            raise FileNotFoundError(f"No SSH key for account '{account_name}'")

        entry = self._build_config_entry(host_alias, actual_host, str(key_path))

        # Read existing config (if any)
        existing = self._read_ssh_config()

        if host_alias in existing:
            # Replace existing block
            updated = self._replace_config_block(existing, host_alias, entry)
        else:
            # Append
            updated = existing.rstrip("\n") + "\n\n" + entry + "\n"

        self._write_ssh_config(updated)
        print_success(f"SSH config entry added for host alias: {host_alias}")
        return host_alias

    def remove_ssh_config_entry(self, host_alias: str) -> None:
        """Remove the SSH config block that matches *host_alias*."""
        existing = self._read_ssh_config()
        if host_alias not in existing:
            print_warning(f"No SSH config entry found for '{host_alias}'")
            return

        updated = self._remove_config_block(existing, host_alias)
        self._write_ssh_config(updated)
        print_success(f"SSH config entry removed for: {host_alias}")

    def remove_ssh_keys(self, account_name: str) -> None:
        """Delete the SSH key pair associated with the account."""
        for suffix in ("", ".pub"):
            for key_type in ("ed25519", "rsa", "ecdsa"):
                path = self.ssh_dir / f"id_{key_type}_{account_name}{suffix}"
                if path.exists():
                    path.unlink()
                    print_success(f"Deleted: {path}")

    def get_public_key(self, account_name: str) -> Optional[str]:
        """Return the public-key contents for the given account."""
        for key_type in ("ed25519", "rsa", "ecdsa"):
            pub = self.ssh_dir / f"id_{key_type}_{account_name}.pub"
            if pub.exists():
                return pub.read_text().strip()
        return None

    def add_key_to_agent(self, account_name: str) -> None:
        """Add the private key to the running ssh-agent."""
        key = self._find_key_for_account(account_name)
        if key is None:
            print_error(f"No SSH key found for account '{account_name}'")
            return
        run_command(["ssh-add", str(key)], check=False)
        print_success(f"Key added to ssh-agent: {key}")

    def list_ssh_keys(self) -> list[dict]:
        """List all mgit-managed SSH keys found in ~/.ssh."""
        keys = []
        for path in sorted(self.ssh_dir.glob("id_*")):
            if path.suffix == ".pub":
                continue
            name = path.name
            # Expected pattern: id_<type>_<account_name>
            parts = name.split("_", 2)
            if len(parts) == 3:
                keys.append(
                    {
                        "account": parts[2],
                        "type": parts[1],
                        "path": str(path),
                        "public_key_path": str(path) + ".pub",
                    }
                )
        return keys

    def test_ssh_connection(self, host_alias: str) -> bool:
        """Test the SSH connection to verify it works."""
        result = run_command(
            ["ssh", "-T", f"git@{host_alias}"],
            check=False,
        )
        # GitHub returns exit code 1 with "successfully authenticated"
        output = (result.stdout or "") + (result.stderr or "")
        success = "successfully authenticated" in output.lower() or result.returncode == 0
        if success:
            print_success(f"SSH connection test passed for {host_alias}")
        else:
            print_error(f"SSH connection test failed for {host_alias}")
        return success

    # ---- Private helpers ----

    def _find_key_for_account(self, account_name: str) -> Optional[Path]:
        for key_type in ("ed25519", "rsa", "ecdsa"):
            path = self.ssh_dir / f"id_{key_type}_{account_name}"
            if path.exists():
                return path
        return None

    @staticmethod
    def _build_config_entry(host_alias: str, hostname: str, identity_file: str) -> str:
        return (
            f"# mgit-managed: {host_alias}\n"
            f"Host {host_alias}\n"
            f"    HostName {hostname}\n"
            f"    User git\n"
            f"    IdentityFile {identity_file}\n"
            f"    IdentitiesOnly yes\n"
            f"# end-mgit: {host_alias}"
        )

    def _read_ssh_config(self) -> str:
        if self.ssh_config_file.exists():
            return self.ssh_config_file.read_text()
        return ""

    def _write_ssh_config(self, content: str) -> None:
        self.ssh_config_file.write_text(content)
        os.chmod(self.ssh_config_file, 0o600)

    @staticmethod
    def _replace_config_block(config: str, host_alias: str, new_entry: str) -> str:
        lines = config.split("\n")
        result, skip = [], False
        for line in lines:
            if f"# mgit-managed: {host_alias}" in line:
                skip = True
                continue
            if f"# end-mgit: {host_alias}" in line:
                skip = False
                result.append(new_entry)
                continue
            if not skip:
                result.append(line)
        return "\n".join(result)

    @staticmethod
    def _remove_config_block(config: str, host_alias: str) -> str:
        lines = config.split("\n")
        result, skip = [], False
        for line in lines:
            if f"# mgit-managed: {host_alias}" in line:
                skip = True
                continue
            if f"# end-mgit: {host_alias}" in line:
                skip = False
                continue
            if not skip:
                result.append(line)
        return "\n".join(result)