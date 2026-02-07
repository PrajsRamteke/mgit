"""
Manages local and global Git configuration so the right user.name,
user.email, and SSH settings are applied per repository.
"""

import os
from pathlib import Path
from typing import Optional

from utils import (
    run_command,
    print_success,
    print_error,
    print_info,
    is_git_repo,
    console,
)
from account_manager import Account


class GitConfigManager:
    """Read and write Git configuration at global and local scope."""

    # ---- Global config ----

    @staticmethod
    def set_global_config(account: Account) -> None:
        """Apply the account's identity to the global Git config."""
        run_command(["git", "config", "--global", "user.name", account.git_username])
        run_command(["git", "config", "--global", "user.email", account.git_email])

        if account.signing_key:
            run_command(
                ["git", "config", "--global", "user.signingkey", account.signing_key]
            )
            run_command(
                ["git", "config", "--global", "commit.gpgsign", "true"]
            )

        print_success(
            f"Global Git config set to: {account.git_username} <{account.git_email}>"
        )

    # ---- Local (per-repo) config ----

    @staticmethod
    def set_local_config(account: Account, repo_path: Optional[str] = None) -> None:
        """Apply the account's identity to the local (repo) Git config."""
        cwd = repo_path or os.getcwd()
        if not is_git_repo(cwd):
            print_error(f"'{cwd}' is not a Git repository.")
            raise RuntimeError("Not a git repository")

        run_command(
            ["git", "config", "--local", "user.name", account.git_username], cwd=cwd
        )
        run_command(
            ["git", "config", "--local", "user.email", account.git_email], cwd=cwd
        )

        if account.signing_key:
            run_command(
                ["git", "config", "--local", "user.signingkey", account.signing_key],
                cwd=cwd,
            )
            run_command(
                ["git", "config", "--local", "commit.gpgsign", "true"], cwd=cwd
            )

        print_success(
            f"Local Git config for '{cwd}' set to: "
            f"{account.git_username} <{account.git_email}>"
        )

    # ---- Conditional includes (directory-based) ----

    @staticmethod
    def setup_conditional_include(
        directory: str,
        account: Account,
    ) -> None:
        """
        Configure a Git conditional include so that all repos under
        *directory* automatically use the given account's identity.

        This writes a small `.gitconfig` file inside the directory and
        adds an `includeIf` directive to the global Git config.
        """
        dir_path = Path(directory).expanduser().resolve()
        dir_path.mkdir(parents=True, exist_ok=True)

        # Ensure trailing slash (required by Git for includeIf)
        gitdir_pattern = str(dir_path) + "/"

        # Write per-directory gitconfig
        dir_gitconfig = dir_path / ".gitconfig"
        config_content = (
            f"[user]\n"
            f"    name = {account.git_username}\n"
            f"    email = {account.git_email}\n"
        )
        if account.signing_key:
            config_content += f"    signingkey = {account.signing_key}\n"
            config_content += "[commit]\n    gpgsign = true\n"

        # Set the SSH command to use the right key
        config_content += (
            f"[core]\n"
            f"    sshCommand = ssh -i {account.ssh_key_path} -o IdentitiesOnly=yes\n"
        )

        dir_gitconfig.write_text(config_content)
        print_success(f"Created directory gitconfig: {dir_gitconfig}")

        # Add includeIf to global config
        run_command(
            [
                "git",
                "config",
                "--global",
                f"includeIf.gitdir:{gitdir_pattern}.path",
                str(dir_gitconfig),
            ]
        )
        print_success(
            f"Conditional include added: repos under '{dir_path}' → "
            f"{account.git_username} <{account.git_email}>"
        )

    # ---- URL rewriting ----

    @staticmethod
    def setup_url_rewrite(account: Account) -> None:
        """
        Configure `url.<base>.insteadOf` so that cloning from the
        provider automatically uses the correct SSH host alias.

        Example for GitHub:
            git@github.com-personal:user/repo.git
        instead of
            git@github.com:user/repo.git
        """
        from ssh_manager import PROVIDER_HOSTS

        actual_host = PROVIDER_HOSTS.get(account.provider, account.custom_host)
        if actual_host is None:
            print_error("Cannot determine host for URL rewrite.")
            return

        run_command(
            [
                "git",
                "config",
                "--global",
                f"url.git@{account.host_alias}:.insteadOf",
                f"git@{actual_host}:",
            ]
        )
        print_success(
            f"URL rewrite: git@{actual_host}: → git@{account.host_alias}:"
        )

    # ---- Clone helper ----

    @staticmethod
    def clone_with_account(
        account: Account,
        repo_url: str,
        destination: Optional[str] = None,
    ) -> None:
        """
        Clone a repository using the SSH host alias of the given account,
        then set the local config inside the cloned repo.
        """
        from ssh_manager import PROVIDER_HOSTS

        actual_host = PROVIDER_HOSTS.get(account.provider, account.custom_host)
        # Rewrite URL to use the host alias
        modified_url = repo_url.replace(
            f"git@{actual_host}:", f"git@{account.host_alias}:"
        )

        cmd = ["git", "clone", modified_url]
        if destination:
            cmd.append(destination)

        print_info(f"Cloning with account '{account.name}': {modified_url}")
        run_command(cmd, capture_output=False)

        # Determine cloned directory name
        if destination:
            repo_dir = destination
        else:
            repo_dir = modified_url.split("/")[-1].replace(".git", "")

        GitConfigManager.set_local_config(account, repo_dir)

    # ---- Display helpers ----

    @staticmethod
    def show_current_config(repo_path: Optional[str] = None) -> None:
        """Pretty-print the effective Git user config for the given scope."""
        cwd = repo_path or os.getcwd()

        console.print("\n[bold]Global Git Config:[/bold]")
        for key in ("user.name", "user.email"):
            res = run_command(
                ["git", "config", "--global", key], check=False
            )
            value = res.stdout.strip() if res.returncode == 0 else "(not set)"
            console.print(f"  {key}: {value}")

        if is_git_repo(cwd):
            console.print(f"\n[bold]Local Git Config ({cwd}):[/bold]")
            for key in ("user.name", "user.email"):
                res = run_command(
                    ["git", "config", "--local", key], check=False, cwd=cwd
                )
                value = res.stdout.strip() if res.returncode == 0 else "(not set)"
                console.print(f"  {key}: {value}")
        else:
            console.print(f"\n[dim]('{cwd}' is not a Git repository)[/dim]")