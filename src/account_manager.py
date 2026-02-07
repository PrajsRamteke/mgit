"""
Account persistence – stores and retrieves Git account profiles in
~/.mgit/config.yaml.
"""

from pathlib import Path
from typing import Optional

import yaml

from .utils import (
    get_mgit_config_file,
    validate_email,
    validate_account_name,
    print_success,
    print_error,
    print_warning,
)


class Account:
    """Data class representing a single Git account profile."""

    def __init__(
        self,
        name: str,
        git_username: str,
        git_email: str,
        provider: str,
        host_alias: str,
        ssh_key_path: str,
        signing_key: Optional[str] = None,
        custom_host: Optional[str] = None,
        is_default: bool = False,
    ):
        self.name = name
        self.git_username = git_username
        self.git_email = git_email
        self.provider = provider
        self.host_alias = host_alias
        self.ssh_key_path = ssh_key_path
        self.signing_key = signing_key
        self.custom_host = custom_host
        self.is_default = is_default

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "git_username": self.git_username,
            "git_email": self.git_email,
            "provider": self.provider,
            "host_alias": self.host_alias,
            "ssh_key_path": self.ssh_key_path,
            "signing_key": self.signing_key,
            "custom_host": self.custom_host,
            "is_default": self.is_default,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        return cls(**data)

    def __repr__(self) -> str:
        default_tag = " [DEFAULT]" if self.is_default else ""
        return (
            f"Account({self.name} | {self.git_username} <{self.git_email}> "
            f"| {self.provider}{default_tag})"
        )


class AccountManager:
    """CRUD operations on the account store (~/.mgit/config.yaml)."""

    def __init__(self):
        self.config_file: Path = get_mgit_config_file()
        self.accounts: dict[str, Account] = {}
        self._load()

    # ---- Public API ----

    def add_account(
        self,
        name: str,
        git_username: str,
        git_email: str,
        provider: str,
        host_alias: str,
        ssh_key_path: str,
        signing_key: Optional[str] = None,
        custom_host: Optional[str] = None,
        is_default: bool = False,
    ) -> Account:
        """Validate, create, and persist a new account."""
        # --- Validation ---
        if not validate_account_name(name):
            raise ValueError(
                f"Invalid account name '{name}'. "
                "Use only alphanumerics, hyphens, and underscores."
            )

        if not validate_email(git_email):
            raise ValueError(f"Invalid email address: {git_email}")

        if name in self.accounts:
            raise ValueError(f"Account '{name}' already exists. Use a different name.")

        # If this is the first account, make it default
        if not self.accounts:
            is_default = True

        # Clear old default when a new default is set
        if is_default:
            for acct in self.accounts.values():
                acct.is_default = False

        account = Account(
            name=name,
            git_username=git_username,
            git_email=git_email,
            provider=provider,
            host_alias=host_alias,
            ssh_key_path=ssh_key_path,
            signing_key=signing_key,
            custom_host=custom_host,
            is_default=is_default,
        )
        self.accounts[name] = account
        self._save()
        print_success(f"Account '{name}' added successfully.")
        return account

    def remove_account(self, name: str) -> None:
        if name not in self.accounts:
            print_error(f"Account '{name}' not found.")
            raise KeyError(name)
        del self.accounts[name]
        self._save()
        print_success(f"Account '{name}' removed.")

    def get_account(self, name: str) -> Optional[Account]:
        return self.accounts.get(name)

    def get_default_account(self) -> Optional[Account]:
        for acct in self.accounts.values():
            if acct.is_default:
                return acct
        # Fall back to the first account
        return next(iter(self.accounts.values()), None)

    def set_default(self, name: str) -> None:
        if name not in self.accounts:
            print_error(f"Account '{name}' not found.")
            raise KeyError(name)
        for acct in self.accounts.values():
            acct.is_default = acct.name == name
        self._save()
        print_success(f"Default account set to '{name}'.")

    def list_accounts(self) -> list[Account]:
        return list(self.accounts.values())

    def update_account(self, name: str, **kwargs) -> Account:
        if name not in self.accounts:
            raise KeyError(f"Account '{name}' not found.")

        account = self.accounts[name]
        for key, value in kwargs.items():
            if hasattr(account, key) and value is not None:
                setattr(account, key, value)
        self._save()
        print_success(f"Account '{name}' updated.")
        return account

    # ---- Persistence ----

    def _load(self) -> None:
        if not self.config_file.exists():
            self.accounts = {}
            return
        try:
            data = yaml.safe_load(self.config_file.read_text()) or {}
            raw_accounts = data.get("accounts", {})
            self.accounts = {
                name: Account.from_dict(info)
                for name, info in raw_accounts.items()
            }
        except yaml.YAMLError as e:
            print_error(f"Failed to parse config file: {e}")
            self.accounts = {}

    def _save(self) -> None:
        data = {
            "version": "1.0",
            "accounts": {
                name: acct.to_dict() for name, acct in self.accounts.items()
            },
        }
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(yaml.dump(data, default_flow_style=False))