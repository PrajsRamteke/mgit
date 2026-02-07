# 🔐 Multi-Git Manager (mgit)

Manage multiple Git accounts on a single machine effortlessly. Generate SSH keys, configure SSH aliases, and switch between Git identities with ease.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-git-manager.git
cd multi-git-manager

# Install the package
pip install -e .
```

---

## 🚀 Quick Start Guide

### Step 1: Add a New Account Using Username

Simply provide your GitHub/GitLab username — mgit automatically fetches your name and email!

```bash
# Basic usage - just provide username
mgit add YourGitHubUsername

# Add as default account
mgit add YourGitHubUsername -d

# Add with custom profile name
mgit add YourGitHubUsername -n myprofile

# Add GitLab account
mgit add YourGitLabUsername -p gitlab

# Add Bitbucket account
mgit add YourBitbucketUsername -p bitbucket
```

**Example:**
```bash
mgit add PrajsRamteke -d
```

**Output:**
```
ℹ Fetching user details from github...
  Name: PRAJWAL BHIMRAO RAMTEKE
  Email: 115864844+PrajsRamteke@users.noreply.github.com
✓ Profile 'PrajsRamteke' created successfully!
```

---

### Step 2: Get Your SSH Public Key

After adding an account, mgit generates an SSH key pair. Get your public key to add to GitHub/GitLab:

```bash
# Show SSH public key for a profile
mgit key YourProfileName

# Or use the full command
mgit show-key YourProfileName
```

**Example:**
```bash
mgit key PrajsRamteke
```

**Output:**
```
Public key for 'PrajsRamteke':

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG... your@email.com
```

**📋 Copy this entire key** — you'll need it for the next step!

---

### Step 3: Add SSH Key to GitHub

1. **Open GitHub SSH Settings**
   - Go to: [https://github.com/settings/keys](https://github.com/settings/keys)
   - Or: GitHub → Settings → SSH and GPG keys

2. **Click "New SSH key"**

3. **Fill in the details:**
   - **Title:** Give it a descriptive name (e.g., "MacBook Pro - Work")
   - **Key type:** Authentication Key
   - **Key:** Paste your public key (from Step 2)

4. **Click "Add SSH key"**

5. **Confirm** with your GitHub password if prompted

> **For GitLab:** Go to [https://gitlab.com/-/user_settings/ssh_keys](https://gitlab.com/-/user_settings/ssh_keys)
>
> **For Bitbucket:** Go to Bitbucket → Personal Settings → SSH keys

---

### Step 4: Test the Connection

Verify that your SSH key is properly configured:

```bash
mgit test YourProfileName
```

**Example:**
```bash
mgit test PrajsRamteke
```

**Expected Output:**
```
✓ SSH connection successful for 'PrajsRamteke'
  Hi PrajsRamteke! You've successfully authenticated.
```

---

### Step 5: Use Your Account

Now you can use your configured account!

#### Switch to a Profile (Global)
```bash
mgit use YourProfileName
# or
mgit switch YourProfileName
```

#### Switch for Current Repository Only
```bash
mgit use YourProfileName -l
```

#### Clone a Repository with Specific Profile
```bash
mgit clone YourProfileName git@github.com:username/repo.git
```

---

## 📚 All Commands Reference

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

## 🎯 Common Examples

### Add Multiple Accounts

```bash
# Personal GitHub (set as default)
mgit add johndoe -d

# Work GitHub
mgit add john-doe-company -n work

# GitLab account
mgit add jdoe -p gitlab -n freelance
```

### View All Your Accounts

```bash
mgit ls
```

**Output:**
```
┌───────────┬──────────────────┬─────────────────────┬──────────┬───────────────────────────┬─────────┐
│ Name      │ Username         │ Email               │ Provider │ Host Alias                │ Default │
├───────────┼──────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────┤
│ johndoe   │ johndoe          │ john@gmail.com      │ github   │ github.com-johndoe        │    ✓    │
│ work      │ john-doe-company │ john@company.com    │ github   │ github.com-work           │         │
│ freelance │ jdoe             │ jdoe@gitlab.com     │ gitlab   │ gitlab.com-freelance      │         │
└───────────┴──────────────────┴─────────────────────┴──────────┴───────────────────────────┴─────────┘
```

### Check Current Configuration

```bash
mgit current
```

### Preview User Info Before Adding

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

### Set Up Workspace Auto-Switching

```bash
# Automatically use 'work' profile in ~/work directory
mgit workspace work ~/work

# Automatically use 'personal' profile in ~/personal directory
mgit workspace personal ~/personal
```

---

## 🔧 Troubleshooting

### SSH Connection Failed

1. Make sure you added the SSH key to GitHub/GitLab
2. Run `mgit key <name>` and verify the key matches what's on GitHub
3. Check if SSH agent is running: `eval "$(ssh-agent -s)"`

### Permission Denied

```bash
# Test the connection
mgit test YourProfileName

# If it fails, try adding the key to SSH agent manually
ssh-add ~/.ssh/id_ed25519_YourProfileName
```

### Email Not Public

If your email is not public on GitHub, mgit will automatically use your GitHub noreply email:
```
⚠ Email not public. Using: 12345678+username@users.noreply.github.com
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.