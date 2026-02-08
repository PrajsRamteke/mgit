# 🔐 Multi-Git Manager (mgit)

Manage multiple Git accounts on a single machine effortlessly. Generate SSH keys, configure SSH aliases, and switch between Git identities with ease.

---

🌐 **Live Demo:** [![Website](https://img.shields.io/website?label=mgit.netlify.app&style=flat-square&url=https%3A%2F%2Fmgit.netlify.app%2F)](https://mgit.netlify.app/)

---

## 📦 Installation

**Quick install (recommended: Copy one by one and paste in terminal):**

```bash
curl -fsSL https://raw.githubusercontent.com/PrajsRamteke/mgit/main/install.sh | bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
mgit --version
mgit --help
```

**Alternative: Install with pipx**

```bash
# Install pipx (if needed)
brew install pipx
pipx ensurepath

# Install mgit
pipx install git+https://github.com/PrajsRamteke/mgit.git
```

**Verify installation:**
```bash
mgit --version
mgit --help
```

---

## 🚀 Quick Start

### Step 1: Add Your Account

Just provide your GitHub/GitLab username — mgit automatically fetches your name and email!

```bash
# Add GitHub account (set as default)
mgit add YourGitHubUsername -d

# Add with custom profile name
mgit add YourGitHubUsername -n work

# Add GitLab account
mgit add YourGitLabUsername -p gitlab

# Add Bitbucket account
mgit add YourBitbucketUsername -p bitbucket
```

**Example output:**
```
ℹ Fetching user details from github...
  Name: Your Name
  Email: your@email.com
✓ Profile 'YourGitHubUsername' created successfully!
```

### Step 2: Get Your SSH Public Key

Copy your public key to add it to GitHub/GitLab:

```bash
mgit key YourProfileName
```

**Output:**
```
Public key for 'YourProfileName':

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG... your@email.com
```

📋 **Copy the entire key** — you'll need it next!

### Step 3: Add SSH Key to GitHub/GitLab

**GitHub:**
1. Go to [GitHub SSH Settings](https://github.com/settings/keys)
2. Click "New SSH key"
3. Paste your key and save

**GitLab:** [GitLab SSH Keys](https://gitlab.com/-/user_settings/ssh_keys)  
**Bitbucket:** Bitbucket → Personal Settings → SSH keys

### Step 4: Test Connection

```bash
mgit test YourProfileName
```

**Expected output:**
```
✓ SSH connection successful for 'YourProfileName'
  Hi YourProfileName! You've successfully authenticated.
```

### Step 5: Start Using

```bash
# Switch to a profile (global)
mgit use YourProfileName

# Switch for current repository only
mgit use YourProfileName -l

# Clone with specific profile
mgit clone YourProfileName git@github.com:username/repo.git
```

---

## 📚 Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `mgit add <username>` | - | Add a new account profile |
| `mgit remove <name>` | `mgit rm` | Remove a profile |
| `mgit list` | `mgit ls` | List all profiles |
| `mgit switch <name>` | `mgit use` | Switch to a profile |
| `mgit show-key <name>` | `mgit key` | Show SSH public key |
| `mgit test <name>` | - | Test SSH connection |
| `mgit current` | - | Show current config |
| `mgit clone <name> <url>` | - | Clone with specific profile |
| `mgit info <username>` | - | Preview user info without adding |
| `mgit workspace <name> <dir>` | - | Set workspace for auto-switching |

---

## 🎯 Examples

### Add Multiple Accounts

```bash
# Personal GitHub (default)
mgit add johndoe -d

# Work GitHub
mgit add john-doe-company -n work

# GitLab account
mgit add jdoe -p gitlab -n freelance
```

### View All Accounts

```bash
mgit ls
```

### Check Current Configuration

```bash
mgit current
```

### Preview User Info

```bash
mgit info SomeUsername
mgit info SomeUser -p gitlab
```

---

## ⚙️ Advanced Options

### Add Command Options

```bash
mgit add <username> [OPTIONS]

Options:
  -p, --provider    Git provider: github, gitlab, bitbucket, custom (default: github)
  -n, --name        Profile name (default: username)
  -e, --email       Override email (auto-fetched if not provided)
  -d, --default     Set as default profile
  -w, --workspace   Workspace directory for auto-switching
  -k, --key-type    SSH key type: ed25519, rsa (default: ed25519)
  --passphrase      SSH key passphrase
  --signing-key     GPG signing key ID
  --custom-host     Custom hostname (required when provider=custom)
```

### Workspace Auto-Switching

Automatically switch profiles based on directory:

```bash
mgit workspace work ~/work
mgit workspace personal ~/personal
```

---

## 🔧 Troubleshooting

### Installation Issues

**macOS "externally-managed-environment" error:**
```bash
# Use the installer script (recommended)
curl -fsSL https://raw.githubusercontent.com/PrajsRamteke/mgit/main/install.sh | bash

# Or use pipx
brew install pipx && pipx ensurepath
pipx install git+https://github.com/PrajsRamteke/mgit.git
```

**`mgit: command not found`:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### SSH Connection Issues

**Connection failed:**
1. Verify SSH key was added to GitHub/GitLab
2. Check key matches: `mgit key <name>`
3. Start SSH agent: `eval "$(ssh-agent -s)"`

**Permission denied:**
```bash
mgit test YourProfileName
ssh-add ~/.ssh/id_ed25519_YourProfileName
```

**Email not public:**
mgit automatically uses GitHub noreply email if your email isn't public.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
