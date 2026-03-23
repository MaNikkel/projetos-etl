#!/usr/bin/env bash
# install-java.sh — Install Java 21 + Maven on Amazon Linux 2023
set -euo pipefail

echo "=== Installing Java 21 + Maven ==="

# Java 21 (Amazon Corretto)
sudo dnf install -y java-21-amazon-corretto-devel

# Maven
sudo dnf install -y maven

# Verify
echo ""
echo "--- Installed versions ---"
java -version
mvn -version

echo ""
echo "=== Java setup complete ==="
