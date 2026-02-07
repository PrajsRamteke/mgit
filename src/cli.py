"""
Command-line interface for the Multi-Git Manager (mgit).
"""

import sys
from typing import Optional

import click
from rich.console import Console

from profile_manager import ProfileManager
from utils import (
    print_header,
    print_success,
    print_error,
    print_info,
    print_warning,
    fetch_provider_user,
    generate_noreply_email,
)

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
    
    \b
    Quick Start:
      mgit add PrajsRamteke              # Add GitHub account (auto-fetches details)
      mgit add PrajsRamteke -d           # Add as default account
      mgit add user -p gitlab            # Add GitLab account
      mgit ls                            # List all profiles
      mgit use work                      # Switch to work profile
      mgit key personal                  # Show SSH public key
    """


# ── add ─────────────────────────────────────────────────────────────────────

@main.command()
@click.argument("username")
@click.option(
    "--provider", "-p",
    type=click.Choice(["github", "gitlab", "bitbucket", "custom"]),
    default="github",
    help="Git hosting provider (default: github)",
)
@click.option("--name", "-n", help="Profile name (default: username)")
@click.option("--email", "-e", help="Override email (auto-fetched if not provided)")
@click.option("--default", "-d", "is_default", is_flag=True, help="Set as default profile")
@click.option("--workspace", "-w", help="Workspace directory for auto-switching")
@click.option("--custom-host", help="Custom hostname (required when provider=custom)")
@click.option("--key-type", "-k", type=click.Choice(["ed25519", "rsa"]), default="ed25519", help="SSH key type")
@click.option("--passphrase", default="", help="SSH key passphrase")
@click.option("--signing-key", help="GPG signing key ID")
def add(
    username: str,
    provider: str,
    name: Optional[str],
    email: Optional[str],
    is_default: bool,
    workspace: Optional[str],
    custom_host: Optional[str],
    key_type: str,
    passphrase: str,
    signing_key: Optional[str],
):
    """
    Add a new Git account profile.

    \b
    Examples:
      mgit add PrajsRamteke              # Add GitHub user (auto-fetches name/email)
      mgit add PrajsRamteke -d           # Add as default profile
      mgit add user -p gitlab            # Add GitLab user
      mgit add user -n work -w ~/work    # Add with custom profile name & workspace
      mgit add user -e my@email.com      # Override email
    """
    try:
        # Use username as profile name if not provided
        profile_name = name or username
        
        # Fetch user details from provider API
        if provider != "custom":
            print_info(f"Fetching user details from {provider}...")
            try:
                user_data = fetch_provider_user(username, provider)
                git_username = user_data.get("name") or username
                
                # Use provided email or fetched email or generate noreply
                if email:
                    git_email = email
                elif user_data.get("email"):
                    git_email = user_data["email"]
                else:
                    # Generate noreply email
                    user_id = user_data.get("id", 0)
                    git_email = generate_noreply_email(username, user_id, provider)
                    print_warning(f"Email not public. Using: {git_email}")
                
                console.print(f"  [dim]Name:[/dim] {git_username}")
                console.print(f"  [dim]Email:[/dim] {git_email}")
                
            except ValueError as e:
                print_error(str(e))
                sys.exit(1)
        else:
            # Custom provider - require email
            if not email:
                print_error("Email required for custom provider: use --email/-e")
                sys.exit(1)
            if not custom_host:
                print_error("Custom host required: use --custom-host")
                sys.exit(1)
            git_username = username
            git_email = email
        
        # Create the profile
        pm.add_profile(
            name=profile_name,
            git_username=git_username,
            git_email=git_email,
            provider=provider,
            custom_host=custom_host,
            key_type=key_type,
            passphrase=passphrase,
            signing_key=signing_key,
            is_default=is_default,
            workspace_dir=workspace,
        )
        
    except (ValueError, FileNotFoundError) as e:
        print_error(str(e))
        sys.exit(1)


# ── remove / rm ─────────────────────────────────────────────────────────────

@main.command()
@click.argument("name")
@click.option("--keep-keys", "-k", is_flag=True, help="Keep SSH keys on disk")
def remove(name: str, keep_keys: bool):
    """Remove a Git account profile."""
    pm.remove_profile(name, delete_keys=not keep_keys)


@main.command(name="rm", hidden=True)
@click.argument("name")
@click.option("--keep-keys", "-k", is_flag=True, help="Keep SSH keys on disk")
def rm(name: str, keep_keys: bool):
    """Alias for remove."""
    pm.remove_profile(name, delete_keys=not keep_keys)


# ── switch / use ────────────────────────────────────────────────────────────

@main.command()
@click.argument("name")
@click.option("--local", "-l", "is_local", is_flag=True, help="Apply to current repo only")
@click.option("--repo-path", "-r", help="Repository path (for local scope)")
def switch(name: str, is_local: bool, repo_path: Optional[str]):
    """
    Switch to a different Git account profile.

    \b
    Examples:
      mgit switch work          # Switch globally
      mgit switch personal -l   # Switch for current repo only
    """
    scope = "local" if is_local else "global"
    pm.switch_profile(name, scope=scope, repo_path=repo_path)


@main.command(name="use", hidden=True)
@click.argument("name")
@click.option("--local", "-l", "is_local", is_flag=True, help="Apply to current repo only")
@click.option("--repo-path", "-r", help="Repository path (for local scope)")
def use(name: str, is_local: bool, repo_path: Optional[str]):
    """Alias for switch."""
    scope = "local" if is_local else "global"
    pm.switch_profile(name, scope=scope, repo_path=repo_path)


# ── list / ls ───────────────────────────────────────────────────────────────

@main.command(name="list")
def list_profiles():
    """List all configured Git account profiles."""
    pm.list_profiles()


@main.command(name="ls", hidden=True)
def ls():
    """Alias for list."""
    pm.list_profiles()


# ── current ─────────────────────────────────────────────────────────────────

@main.command()
def current():
    """Show the current Git configuration and active profile."""
    pm.show_current()


# ── clone ───────────────────────────────────────────────────────────────────

@main.command()
@click.argument("name")
@click.argument("repo_url")
@click.argument("destination", required=False)
def clone(name: str, repo_url: str, destination: Optional[str]):
    """
    Clone a repository using a specific Git account profile.

    \b
    Example:
      mgit clone work git@github.com:company/repo.git
    """
    pm.clone_repo(name, repo_url, destination)


# ── test ────────────────────────────────────────────────────────────────────

@main.command()
@click.argument("name")
def test(name: str):
    """Test SSH connection for a Git account profile."""
    pm.test_connection(name)


# ── workspace ───────────────────────────────────────────────────────────────

@main.command()
@click.argument("name")
@click.argument("directory")
def workspace(name: str, directory: str):
    """
    Set up a workspace directory for automatic profile switching.

    \b
    Example:
      mgit workspace work ~/work
    """
    pm.setup_workspace(name, directory)


# ── show-key / key ──────────────────────────────────────────────────────────

@main.command(name="show-key")
@click.argument("name")
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
        print_error(f"No SSH key found for '{name}'")


@main.command(name="key", hidden=True)
@click.argument("name")
def key(name: str):
    """Alias for show-key."""
    from ssh_manager import SSHManager

    ssh = SSHManager()
    pub = ssh.get_public_key(name)
    if pub:
        console.print(f"\n[bold]Public key for '{name}':[/bold]\n")
        console.print(pub)
        console.print()
    else:
        print_error(f"No SSH key found for '{name}'")


# ── info (new) ──────────────────────────────────────────────────────────────

@main.command()
@click.argument("username")
@click.option(
    "--provider", "-p",
    type=click.Choice(["github", "gitlab", "bitbucket"]),
    default="github",
    help="Git hosting provider",
)
def info(username: str, provider: str):
    """
    Fetch and display user info from a Git provider (without adding).

    \b
    Example:
      mgit info PrajsRamteke
      mgit info someuser -p gitlab
    """
    try:
        print_info(f"Fetching {provider} user: {username}")
        user_data = fetch_provider_user(username, provider)
        
        console.print()
        console.print(f"[bold cyan]User Info ({provider})[/bold cyan]")
        console.print(f"  [dim]Login:[/dim]    {user_data.get('login')}")
        console.print(f"  [dim]Name:[/dim]     {user_data.get('name')}")
        console.print(f"  [dim]ID:[/dim]       {user_data.get('id')}")
        
        if user_data.get('email'):
            console.print(f"  [dim]Email:[/dim]    {user_data.get('email')}")
        else:
            noreply = generate_noreply_email(username, user_data.get('id', 0), provider)
            console.print(f"  [dim]Email:[/dim]    [yellow](not public)[/yellow]")
            console.print(f"  [dim]No-reply:[/dim] {noreply}")
        
        if user_data.get('bio'):
            console.print(f"  [dim]Bio:[/dim]      {user_data.get('bio')}")
        if user_data.get('html_url'):
            console.print(f"  [dim]URL:[/dim]      {user_data.get('html_url')}")
        console.print()
        
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()