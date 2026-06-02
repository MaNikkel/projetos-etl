#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
count_script="$script_dir/count-db-rows.sh"
env_file="${1:-$script_dir/.env.ec2}"
interval_seconds=45

if [[ ! -x "$count_script" ]]; then
  echo "Error: '$count_script' is not executable." >&2
  exit 1
fi

play_alert() {
  if command -v afplay >/dev/null 2>&1; then
    afplay /System/Library/Sounds/Glass.aiff >/dev/null 2>&1 || true
    return
  fi

  if command -v say >/dev/null 2>&1; then
    say "Database rows detected" >/dev/null 2>&1 || true
    return
  fi

  printf '\a'
}

while true; do
  row_count="$("$count_script" "$env_file" | tr -d '[:space:]')"
  timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

  echo "[$timestamp] Row count: $row_count"

  if [[ "$row_count" =~ ^[0-9]+$ ]] && [[ "$row_count" -ne 0 ]]; then
    play_alert
  fi

  sleep "$interval_seconds"
done
