#!/usr/bin/env bash
# install-haskell.sh — Install GHC + Stack on Amazon Linux 2023
set -euo pipefail

echo "=== Installing Haskell (GHC + Stack) ==="

# Dependencies needed to build Haskell packages with C bindings (e.g. postgresql-simple)
sudo dnf install -y gcc gcc-c++ gmp-devel make ncurses-devel perl zlib-devel \
                    postgresql-devel

# Install GHCup (manages GHC + Stack)
echo "Installing GHCup..."
export BOOTSTRAP_HASKELL_NONINTERACTIVE=1
export BOOTSTRAP_HASKELL_INSTALL_STACK=1
export BOOTSTRAP_HASKELL_INSTALL_HLS=0
export BOOTSTRAP_HASKELL_ADJUST_BASHRC=1
curl --proto '=https' --tlsv1.2 -sSf https://get-ghcup.haskell.org | sh

# Load GHCup into current shell
source "$HOME/.ghcup/env"

# Verify
echo ""
echo "--- Installed versions ---"
ghc --version
stack --version

echo ""
echo "=== Haskell setup complete ==="
echo "Run 'source ~/.ghcup/env' or open a new shell to use ghc/stack."
