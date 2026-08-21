#!/bin/bash
# Install consensus-ai from GitHub
set -e

pip install "git+https://github.com/FlossWare/consensus-ai.git"

echo "consensus-ai installed successfully"
echo "Verify: python3 -c 'import consensus_ai; print(consensus_ai.__version__)'"
