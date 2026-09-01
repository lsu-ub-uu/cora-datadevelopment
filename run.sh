#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [args]" >&2
  exit 1
fi

docker run \
  -v ./data:/app/data \
  -v ./logs:/app/logs \
  -v ./reports:/app/reports \
  --env-file .env \
  --network=host \
  cora-datadevelopment "$@"
