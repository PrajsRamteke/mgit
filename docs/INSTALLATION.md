# Installation Guide

## 1) Fastest Setup (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/PrajsRamteke/mgit/main/install.sh | bash
```

What this does:
- Uses `pipx` if available
- Otherwise installs `mgit` in an isolated virtualenv (`~/.local/share/mgit/venv`)
- Links the command to `~/.local/bin/mgit`

## 2) Install with pipx (Manual)

```bash
# macOS
brew install pipx
pipx ensurepath

# install mgit
pipx install git+https://github.com/PrajsRamteke/mgit.git
```

## 3) Install without pipx (Manual venv)

```bash
python3 -m venv ~/.local/share/mgit/venv
~/.local/share/mgit/venv/bin/python -m pip install --upgrade pip
~/.local/share/mgit/venv/bin/python -m pip install git+https://github.com/PrajsRamteke/mgit.git
ln -sf ~/.local/share/mgit/venv/bin/mgit ~/.local/bin/mgit
```

## 4) Ensure `mgit` is on PATH

If `mgit` is not found:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

For bash:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 5) Verify Installation

```bash
mgit --version
mgit --help
```

## Troubleshooting

### `externally-managed-environment` error

This is expected on Homebrew Python (PEP 668) when trying global `pip install`. Use the installer script, `pipx`, or a virtualenv.

### `pip` or `pipx` not found

Use `python3`-based install (virtualenv) or install pipx with Homebrew.
