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