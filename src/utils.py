"""
Utility functions used across the multi-git-manager project.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


# ---------- Path helpers ----------

def get_mgit_config_dir() -> Path:
    """Return the path to the mgit configuration directory (~/.mgit)."""
    config_dir = Path.home() / ".mgit"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_mgit_config_file() -> Path:
    """Return the path to the main mgit configuration file."""
    return get_mgit_config_dir() / "config.yaml"


def get_ssh_dir() -> Path:
    """Return the path to the user's SSH directory (~/.ssh)."""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    return ssh_dir


def get_ssh_config_file() -> Path:
    """Return the path to the SSH config file."""
    return get_ssh_dir() / "config"


# ---------- Command execution ----------

def run_command(
    command: list[str],
    capture_output: bool = True,
    check: bool = True,
    cwd: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """
    Execute a shell command and return the result.

    Parameters
    ----------
    command : list[str]
        The command and its arguments.
    capture_output : bool
        Whether to capture stdout/stderr.
    check : bool
        Whether to raise on non-zero exit code.
    cwd : str, optional
        Working directory for the command.

    Returns
    -------
    subprocess.CompletedProcess
    """
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=check,
            cwd=cwd,
        )
        return result
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error executing command:[/red] {' '.join(command)}")
        console.print(f"[red]stderr:[/red] {e.stderr}")
        raise
    except FileNotFoundError:
        console.print(f"[red]Command not found:[/red] {command[0]}")
        sys.exit(1)


# ---------- Validation helpers ----------

def validate_email(email: str) -> bool:
    """Basic email format validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_account_name(name: str) -> bool:
    """
    Validate that the account/profile name uses only safe characters
    (alphanumerics, hyphens, underscores).
    """
    import re
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, name) is not None


# ---------- Display helpers ----------

def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an informational message in blue."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_header(title: str) -> None:
    """Print a styled header panel."""
    console.print(Panel(Text(title, justify="center"), style="bold blue"))


def confirm_action(message: str) -> bool:
    """Ask the user for a yes/no confirmation."""
    response = console.input(f"[yellow]{message} (y/n):[/yellow] ")
    return response.strip().lower() in ("y", "yes")


# ---------- Git helpers ----------

def get_current_git_user() -> Tuple[Optional[str], Optional[str]]:
    """Return the currently configured global Git (name, email)."""
    try:
        name_result = run_command(
            ["git", "config", "--global", "user.name"], check=False
        )
        email_result = run_command(
            ["git", "config", "--global", "user.email"], check=False
        )
        name = name_result.stdout.strip() if name_result.returncode == 0 else None
        email = email_result.stdout.strip() if email_result.returncode == 0 else None
        return name, email
    except Exception:
        return None, None


def is_git_repo(path: Optional[str] = None) -> bool:
    """Check whether the given (or current) directory is inside a Git repo."""
    try:
        result = run_command(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=False,
            cwd=path,
        )
        return result.returncode == 0
    except Exception:
        return False


# ---------- Provider API helpers ----------

def fetch_github_user(username: str) -> dict:
    """
    Fetch user details from GitHub API.
    
    Returns dict with: login, name, email, id, avatar_url, bio
    Raises ValueError if user not found or API error.
    """
    import requests
    
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            raise ValueError(f"GitHub user '{username}' not found")
        if response.status_code == 403:
            raise ValueError("GitHub API rate limit exceeded. Try again later.")
        response.raise_for_status()
        
        data = response.json()
        return {
            "login": data.get("login"),
            "name": data.get("name") or data.get("login"),
            "email": data.get("email"),
            "id": data.get("id"),
            "avatar_url": data.get("avatar_url"),
            "bio": data.get("bio"),
            "html_url": data.get("html_url"),
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch GitHub user: {e}")


def fetch_gitlab_user(username: str) -> dict:
    """
    Fetch user details from GitLab API.
    
    Returns dict with: username, name, id, avatar_url
    Raises ValueError if user not found or API error.
    """
    import requests
    
    url = f"https://gitlab.com/api/v4/users?username={username}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        users = response.json()
        if not users:
            raise ValueError(f"GitLab user '{username}' not found")
        
        data = users[0]
        return {
            "login": data.get("username"),
            "name": data.get("name") or data.get("username"),
            "id": data.get("id"),
            "avatar_url": data.get("avatar_url"),
            "html_url": data.get("web_url"),
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch GitLab user: {e}")


def fetch_bitbucket_user(username: str) -> dict:
    """
    Fetch user details from Bitbucket API.
    
    Returns dict with: username, display_name, uuid
    Raises ValueError if user not found or API error.
    """
    import requests
    
    url = f"https://api.bitbucket.org/2.0/users/{username}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            raise ValueError(f"Bitbucket user '{username}' not found")
        response.raise_for_status()
        
        data = response.json()
        return {
            "login": data.get("username") or data.get("nickname"),
            "name": data.get("display_name"),
            "id": data.get("uuid"),
            "avatar_url": data.get("links", {}).get("avatar", {}).get("href"),
            "html_url": data.get("links", {}).get("html", {}).get("href"),
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch Bitbucket user: {e}")


def fetch_provider_user(username: str, provider: str) -> dict:
    """
    Fetch user details from the specified Git provider.
    
    Parameters
    ----------
    username : str
        The username to look up.
    provider : str
        One of: github, gitlab, bitbucket
    
    Returns
    -------
    dict with user details (login, name, email, id, etc.)
    """
    if provider == "github":
        return fetch_github_user(username)
    elif provider == "gitlab":
        return fetch_gitlab_user(username)
    elif provider == "bitbucket":
        return fetch_bitbucket_user(username)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def generate_noreply_email(username: str, user_id: int, provider: str) -> str:
    """
    Generate a no-reply email for the given provider.
    
    This is used when the user's email is not public.
    """
    if provider == "github":
        return f"{user_id}+{username}@users.noreply.github.com"
    elif provider == "gitlab":
        return f"{user_id}-{username}@users.noreply.gitlab.com"
    elif provider == "bitbucket":
        return f"{username}@bitbucket.org"
    else:
        return f"{username}@{provider}.com"