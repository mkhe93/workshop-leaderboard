#!/usr/bin/env bash
set -euo pipefail

# ---- Config ----
BASH_PROFILE="${BASH_PROFILE:-$HOME/.bashrc}"
BASE_URL="${LITELLM_BASE_URL:-}"
API_KEY="${LITELLM_ADMIN_KEY:-}"

usage() {
  cat <<'EOF'

Usage:
  ./get_api_key.sh <first_name> <last_name> (optional: <api_key>)

Notes:
  - api_key must start with "sk-"
  - team_alias is generated as: "first_name last_name"
  - team_id and key_alias are generated in lowercase as: "first_name-last_name"
  - sets LITELLM_API_KEY in your $BASH_PROFILE as environment variable

EOF
}

# ---- Args / Validation ----
if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
  usage
  exit 0
fi

FIRST_NAME="${1:-}"
LAST_NAME="${2:-}"

if [[ -z "$FIRST_NAME" || -z "$LAST_NAME" || -z "$API_KEY" ]]; then
  echo "Error: first_name, last_name, and api_key are required."
  usage
  exit 1
fi

if [[ "$API_KEY" != sk-* ]]; then
  echo "Error: api_key must start with 'sk-'."
  exit 1
fi

if [[ -z "$BASE_URL" ]]; then
  echo "No BASE_URL variable set"
  exit 1
fi

echo ""
echo "Obtaining api key for: ${BASE_URL}"
echo ""

# Lowercase + build identifiers
first_lc="$(printf '%s' "$FIRST_NAME" | tr '[:upper:]' '[:lower:]')"
last_lc="$(printf '%s' "$LAST_NAME" | tr '[:upper:]' '[:lower:]')"

TEAM_ALIAS="${FIRST_NAME} ${LAST_NAME}"
TEAM_ID="${first_lc}-${last_lc}"      # lower case required
KEY_ALIAS="${TEAM_ID}"                # lower case required

# Basic URL normalization
BASE_URL="${BASE_URL%/}"

# ---- Helpers ----
require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Error: missing required command: $1"; exit 1; }
}

require_cmd curl
require_cmd jq
require_cmd sed

post_json() {
  # Args: <url> <json_payload>
  local url="$1"
  local payload="$2"

  # Prints: "<http_code>\n<body>"
  curl -sS \
    -X POST "$url" \
    -H 'accept: application/json' \
    -H "x-litellm-api-key: ${API_KEY}" \
    -H 'Content-Type: application/json' \
    -d "$payload" \
    -w $'\n%{http_code}'
}

prompt_yes_no() {
  local prompt="$1"
  local reply
  read -r -p "${prompt} [y/N]: " reply
  [[ "${reply,,}" =~ ^y(es)?$ ]]
}

# ---- 1) Create team ----
team_payload="$(jq -nc --arg team_alias "$TEAM_ALIAS" --arg team_id "$TEAM_ID" \
  '{team_alias: $team_alias, team_id: $team_id}')"

team_raw="$(post_json "${BASE_URL}/team/new" "$team_payload")"
team_code="$(printf '%s' "$team_raw" | tail -n 1)"
team_body="$(printf '%s' "$team_raw" | sed '$d')"

if [[ ! "$team_code" =~ ^2 ]]; then
  err_msg="$(echo "$team_body" | jq -r '.error.message // empty' 2>/dev/null || true)"
  if [[ "$team_code" == "400" && "$err_msg" == *"already exists"* ]]; then
    created_team_id="$TEAM_ID"  # continue; team is assumed to exist
  else
    echo "Error: team creation failed (HTTP $team_code)"
    echo "$team_body" | jq -r '.' 2>/dev/null || echo "$team_body"
    exit 1
  fi
fi

if [[ -z "${created_team_id:-}" ]]; then created_team_id="$(echo "$team_body" | jq -r '.team_id // empty')"; fi

created_team_id="$(echo "$team_body" | jq -r '.team_id // empty' 2>/dev/null || true)"
if [[ -z "$created_team_id" ]]; then
  err_msg="$(echo "$team_body" | jq -r '.error.message // empty' 2>/dev/null || true)"
  if [[ "$team_code" == "400" && "$err_msg" == *"already exists"* ]]; then
    created_team_id="$TEAM_ID"
  else
    echo "Error: team creation response missing .team_id"
    echo "$team_body" | jq -r '.' 2>/dev/null || echo "$team_body"
    exit 1
  fi
fi

# ---- 2) Create key ----
key_payload="$(jq -nc \
  --arg key_alias "$KEY_ALIAS" \
  --arg user_id "default_user_id" \
  --arg duration "10h" \
  --arg team_id "$created_team_id" \
  --argjson models '["all-team-models"]' \
  '{key_alias: $key_alias, user_id: $user_id, duration: $duration, models: $models, team_id: $team_id}')"

key_raw="$(post_json "${BASE_URL}/key/generate" "$key_payload")"
key_code="$(printf '%s' "$key_raw" | tail -n 1)"
key_body="$(printf '%s' "$key_raw" | sed '$d')"

if [[ ! "$key_code" =~ ^2 ]]; then
  err_msg="$(echo "$key_body" | jq -r '.error.message // empty' 2>/dev/null || true)"
  if [[ "$key_code" == "400" && "$err_msg" == *"already exists"* ]]; then
    if prompt_yes_no "Key alias '${KEY_ALIAS}' already exists. Delete and regenerate?"; then
      delete_payload="$(jq -nc --arg alias "$KEY_ALIAS" '{key_aliases: [$alias]}')"
      del_raw="$(post_json "${BASE_URL}/key/delete" "$delete_payload")"
      del_code="$(printf '%s' "$del_raw" | tail -n 1)"
      del_body="$(printf '%s' "$del_raw" | sed '$d')"


      if [[ ! "$del_code" =~ ^2 ]]; then
        echo "Error: key deletion failed (HTTP $del_code)"
        echo "$del_body" | jq -r '.' 2>/dev/null || echo "$del_body"
        exit 1
      fi

      # regenerate
      key_raw="$(post_json "${BASE_URL}/key/generate" "$key_payload")"
      key_code="$(printf '%s' "$key_raw" | tail -n 1)"
      key_body="$(printf '%s' "$key_raw" | sed '$d')"


      if [[ ! "$key_code" =~ ^2 ]]; then
        echo "Error: key regeneration failed (HTTP $key_code)"
        echo "$key_body" | jq -r '.' 2>/dev/null || echo "$key_body"
        exit 1
      fi
    else
      echo "Aborted: existing key not regenerated."
      exit 1
    fi
  else
    echo "Error: key generation failed (HTTP $key_code)"
    echo "$key_body" | jq -r '.' 2>/dev/null || echo "$key_body"
    exit 1
  fi
fi

key_value="$(echo "$key_body" | jq -r '.key // empty')"
if [[ -z "$key_value" ]]; then
  echo "Error: key generation response missing .key"
  echo "$key_body" | jq -r '.' 2>/dev/null || echo "$key_body"
  exit 1
fi

expires="$(echo "$key_body" | jq -r '.expires // empty')"
if [[ -z "$key_value" ]]; then
  echo "Error: key generation response missing .expires"
  echo "$key_body" | jq -r '.' 2>/dev/null || echo "$key_body"
  exit 1
fi

if [[ -f "$BASH_PROFILE" ]]; then
  # remove existing export line (if any), then append the new one
  sed -i.bak '/^[[:space:]]*export[[:space:]]\+LITELLM_API_KEY=/d' "$BASH_PROFILE"
fi
printf '\nexport LITELLM_API_KEY=%q\n' "$key_value" >> "$BASH_PROFILE"

# ---- Output ----
echo ""
echo "########### SUMMARY ##########"
echo "Generated team id: ${created_team_id}"
echo "Generated key id: ${key_value}"
echo "Key expires at: ${expires}"
echo "Exported as LITELLM_API_KEY to: $BASH_PROFILE"
echo ""
echo "########### TODO ##########"
echo "1. (only if working in a devcontainer): add the following to your devcontainer.env: LITELLM_API_KEY=${key_value}"
echo "2. Restart your shell session or run 'source $BASH_PROFILE' to load the new API key into your environment."
echo ""
