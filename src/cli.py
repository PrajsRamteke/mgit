"""
Command-line interface for the Multi-Git Manager (mgit).
"""

import sys
from typing import Optional

import click
from rich.console import Console

from profile_manager import ProfileManager
from utils import print_header

console = Console()
pm = ProfileManager()


# ── Root group ──────────────────────────────────────────────────────────────

@click.group()
@click.version_option(version="1.0.0", prog_name="mgit")
def main():
    """
    mgit — Manage multiple Git accounts on a single machine.

    Generate SSH keys, configure SSH aliases, and switch between
    Git identities effortlessly.
    """


# ── add ─────────────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Unique profile name (e.g. personal, work)")
@click.option("--username", "-u", required=True, help="Git username")
@click.option("--email", "-e", required=True, help="Git email address")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["github", "gitlab", "bitbucket", "custom"]),
    default="github",
    help="Git hosting provider",
)
@click.option("--custom-host", help="Custom hostname (required when provider=custom)")
@click.option(
    "--key-type",
    "-k",
    type=click.Choice(["ed25519", "rsa"]),
    default="ed25519",
    help="SSH key type",
)
@click.option("--passphrase", default="", help="Passphrase for the SSH key (leave empty for none)")
@click.option("--signing-key", help="GPG signing key ID")
@click.option("--default", "is_default", is_flag=True, help="Set as default profile")
@click.option("--workspace", "-w", help="Workspace directory for automatic profile switching")
def add(
    name: str,
    username: str,
    email: str,
    provider: str,
    custom_host: Optional[str],
    key_type: str,
    passphrase: str,
    signing_key: Optional[str],
    is_default: bool,
    workspace: Optional[str],
):
    """Add a new Git account profile."""
    try:
        pm.add_profile(
            name=name,
            git_username=username,
            git_email=email,
            provider=provider,
            custom_host=custom_host,
            key_type=key_type,
            passphrase=passphrase,
            signing_key=signing_key,
            is_default=is_default,
            workspace_dir=workspace,
        )
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


# ── remove ──────────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Profile name to remove")
@click.option("--keep-keys", is_flag=True, help="Keep SSH keys on disk")
def remove(name: str, keep_keys: bool):
    """Remove a Git account profile."""
    pm.remove_profile(name, delete_keys=not keep_keys)


# ── switch ──────────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Profile name to switch to")
@click.option(
    "--scope",
    "-s",
    type=click.Choice(["global", "local"]),
    default="global",
    help="Config scope",
)
@click.option("--repo-path", "-r", help="Repository path (for local scope)")
def switch(name: str, scope: str, repo_path: Optional[str]):
    """Switch to a different Git account profile."""
    pm.switch_profile(name, scope=scope, repo_path=repo_path)


# ── list ────────────────────────────────────────────────────────────────────

@main.command(name="list")
def list_profiles():
    """List all configured Git account profiles."""
    pm.list_profiles()


# ── current ─────────────────────────────────────────────────────────────────

@main.command()
def current():
    """Show the current Git configuration and active profile."""
    pm.show_current()


# ── clone ───────────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Profile name to clone with")
@click.argument("repo_url")
@click.argument("destination", required=False)
def clone(name: str, repo_url: str, destination: Optional[str]):
    """Clone a repository using a specific Git account profile."""
    pm.clone_repo(name, repo_url, destination)


# ── test ────────────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Profile name to test")
def test(name: str):
    """Test SSH connection for a Git account profile."""
    pm.test_connection(name)


# ── workspace ───────────────────────────────────────────────────────────────

@main.command()
@click.option("--name", "-n", required=True, help="Profile name")
@click.option("--directory", "-d", required=True, help="Workspace directory path")
def workspace(name: str, directory: str):
    """Set up a workspace directory for automatic profile switching."""
    pm.setup_workspace(name, directory)


# ── show-key ────────────────────────────────────────────────────────────────

@main.command(name="show-key")
@click.option("--name", "-n", required=True, help="Profile name")
def show_key(name: str):
    """Display the public SSH key for a profile (to add to your Git provider)."""
    from ssh_manager import SSHManager

    ssh = SSHManager()
    pub = ssh.get_public_key(name)
    if pub:
        console.print(f"\n[bold]Public key for '{name}':[/bold]\n")
        console.print(pub)
        console.print()
    else:
        console.print(f"[red]No SSH key found for '{name}'[/red]")


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()