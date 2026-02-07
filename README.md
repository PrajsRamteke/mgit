# 🔀 Multi-Git Manager (mgit)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Effortlessly manage multiple Git accounts on a single machine.**

Ever needed to use your personal GitHub *and* your work GitHub (or GitLab,
Bitbucket, …) on the same computer? `mgit` automates SSH key generation,
SSH config management, and per-repo Git identity so you never push from the
wrong account again.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔑 **SSH Key Management** | Auto-generate & store separate SSH keys per account |
| 📝 **SSH Config** | Automatically maintain `~/.ssh/config` host aliases |
| 🔄 **Profile Switching** | Switch Git identity globally or per-repository |
| 📁 **Workspace Directories** | Conditional includes — repos under a directory auto-use the right identity |
| 📋 **Clone Helper** | `mgit clone` rewrites the remote URL to the correct SSH alias |
| 🧪 **Connection Testing** | Verify SSH connectivity to your provider |
| 🎨 **Beautiful CLI** | Powered by Rich + Click |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-git-manager.git
cd multi-git-manager

# Install in development mode
pip install -e .

# Or install directly
pip install multi-git-manager