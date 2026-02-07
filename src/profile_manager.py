"""
High-level orchestrator – ties together SSH key management, Git config,
and account storage to provide simple "add / switch / remove" workflows.
"""

from typing import Optional

from account_manager import AccountManager, Account
from ssh_manager import SSHManager
from git_config_manager import GitConfigManager
from utils import (
    print_success,
    print_error,
    print_info,
    print_header,
    print_warning,
    confirm_action,
    console,
)


class ProfileManager:
    """End-user workflows for managing Git profiles."""

    def __init__(self):
        self.account_manager = AccountManager()
        self.ssh_manager = SSHManager()
        self.git_config_manager = GitConfigManager()

    # ---- Add ----

    def add_profile(
        self,
        name: str,
        git_username: str,
        git_email: str,
        provider: str = "github",
        custom_host: Optional[str] = None,
        key_type: str = "ed25519",
        passphrase: str = "",
        signing_key: Optional[str] = None,
        is_default: bool = False,
        workspace_dir: Optional[str] = None,
    ) -> Account:
        """
        Full workflow: generate SSH key → update SSH config → store account →
        optionally set up a conditional-include workspace directory.
        """
        print_header(f"Adding Git Profile: {name}")

        # 1. SSH key
        private_key, public_key = self.ssh_manager.generate_ssh_key(
            account_name=name,
            email=git_email,
            key_type=key_type,
            passphrase=passphrase,
        )

        # 2. SSH config entry
        host_alias = self.ssh_manager.add_ssh_config_entry(
            account_name=name,
            provider=provider,
            custom_host=custom_host,
        )

        # 3. Store in mgit config
        account = self.account_manager.add_account(
            name=name,
            git_username=git_username,
            git_email=git_email,
            provider=provider,
            host_alias=host_alias,
            ssh_key_path=str(private_key),
            signing_key=signing_key,
            custom_host=custom_host,
            is_default=is_default,
        )

        # 4. Add key to SSH agent
        self.ssh_manager.add_key_to_agent(name)

        # 5. Conditional include for a workspace directory
        if workspace_dir:
            self.git_config_manager.setup_conditional_include(workspace_dir, account)

        # 6. Show public key
        pub_key_content = self.ssh_manager.get_public_key(name)
        if pub_key_content:
            console.print("\n[bold yellow]Public SSH Key (add this to your Git provider):[/bold yellow]")
            console.print(f"\n{pub_key_content}\n")

        return account

    # ---- Remove ----

    def remove_profile(self, name: str, delete_keys: bool = True) -> None:
        """Remove the profile, SSH config entry, and optionally the SSH keys."""
        print_header(f"Removing Git Profile: {name}")

        account = self.account_manager.get_account(name)
        if account is None:
            print_error(f"Account '{name}' not found.")
            return

        # Confirm
        if not confirm_action(f"Are you sure you want to remove profile '{name}'?"):
            print_info("Cancelled.")
            return

        # SSH config
        self.ssh_manager.remove_ssh_config_entry(account.host_alias)

        # SSH keys
        if delete_keys:
            self.ssh_manager.remove_ssh_keys(name)

        # Account store
        self.account_manager.remove_account(name)

    # ---- Switch ----

    def switch_profile(
        self,
        name: str,
        scope: str = "global",
        repo_path: Optional[str] = None,
    ) -> None:
        """
        Switch to a different Git account.

        scope can be:
          - "global"  → updates ~/.gitconfig
          - "local"   → updates .git/config in the current/given repo
        """
        account = self.account_manager.get_account(name)
        if account is None:
            print_error(f"Account '{name}' not found.")
            return

        print_header(f"Switching to: {name}")

        if scope == "global":
            self.git_config_manager.set_global_config(account)
            self.account_manager.set_default(name)
        elif scope == "local":
            self.git_config_manager.set_local_config(account, repo_path)
        else:
            print_error(f"Unknown scope '{scope}'. Use 'global' or 'local'.")

    # ---- List ----

    def list_profiles(self) -> None:
        """Pretty-print all registered profiles."""
        accounts = self.account_manager.list_accounts()
        if not accounts:
            print_warning("No Git profiles configured. Run `mgit add` to get started.")
            return

        print_header("Registered Git Profiles")
        from rich.table import Table

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Username")
        table.add_column("Email")
        table.add_column("Provider")
        table.add_column("Host Alias")
        table.add_column("Default", justify="center")

        for acct in accounts:
            table.add_row(
                acct.name,
                acct.git_username,
                acct.git_email,
                acct.provider,
                acct.host_alias,
                "✓" if acct.is_default else "",
            )

        console.print(table)

    # ---- Clone ----

    def clone_repo(
        self,
        name: str,
        repo_url: str,
        destination: Optional[str] = None,
    ) -> None:
        """Clone a repo using the specified profile."""
        account = self.account_manager.get_account(name)
        if account is None:
            print_error(f"Account '{name}' not found.")
            return
        self.git_config_manager.clone_with_account(account, repo_url, destination)

    # ---- Show current ----

    def show_current(self) -> None:
        """Show the current Git configuration and active profile."""
        self.git_config_manager.show_current_config()

        default = self.account_manager.get_default_account()
        if default:
            console.print(f"\n[bold]Active mgit profile:[/bold] {default.name}")

    # ---- Test connection ----

    def test_connection(self, name: str) -> bool:
        """Test SSH connectivity for the given profile."""
        account = self.account_manager.get_account(name)
        if account is None:
            print_error(f"Account '{name}' not found.")
            return False
        return self.ssh_manager.test_ssh_connection(account.host_alias)

    # ---- Setup workspace ----

    def setup_workspace(self, name: str, directory: str) -> None:
        """Set up a conditional-include workspace directory for the profile."""
        account = self.account_manager.get_account(name)
        if account is None:
            print_error(f"Account '{name}' not found.")
            return
        self.git_config_manager.setup_conditional_include(directory, account)