#!/usr/bin/env bash
set -euo pipefail

env_file="${1:-.env.ec2}"

if [[ ! -f "$env_file" ]]; then
  echo "Error: env file '$env_file' not found." >&2
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "Error: psql was not found in PATH." >&2
  exit 1
fi

set -a
source "$env_file"
set +a

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:?DB_PORT is required}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

PGPASSWORD="$DB_PASSWORD" psql \
  --host "$DB_HOST" \
  --port "$DB_PORT" \
  --username "$DB_USER" \
  --dbname "$DB_NAME" \
  --tuples-only \
  --no-align \
  --command "SELECT COUNT(*) FROM meteorological_data;"
