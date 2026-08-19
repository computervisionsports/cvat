#!/usr/bin/env bash
#
# Deploy the RF-DETR Nuclio proxy that connects CVAT to cvat-inference.
#
# Required:
#   CVAT_INFERENCE_API_KEY
#
# Optional:
#   CVAT_INFERENCE_API_URL     default: http://host.docker.internal:8000/v1/inference
#   CVAT_INFERENCE_MODEL_NAME  default: scoreboard_general
#
# On Linux, host.docker.internal may not resolve. Run the API in a container on
# the cvat_cvat network, or set CVAT_INFERENCE_API_URL to an address reachable
# from Docker.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
FUNCTION_DIR="$SCRIPT_DIR/nuclio"

: "${CVAT_INFERENCE_API_KEY:?Set CVAT_INFERENCE_API_KEY before deploying}"

CVAT_INFERENCE_API_URL="${CVAT_INFERENCE_API_URL:-http://host.docker.internal:8000/v1/inference}"
CVAT_INFERENCE_MODEL_NAME="${CVAT_INFERENCE_MODEL_NAME:-scoreboard_general}"

# Project creation fails when it already exists; that is safe to ignore.
nuctl create project cvat --platform local 2>/dev/null || true

nuctl deploy \
    --project-name cvat \
    --path "$FUNCTION_DIR" \
    --file "$FUNCTION_DIR/function.yaml" \
    --platform local \
    --env "CVAT_INFERENCE_API_URL=$CVAT_INFERENCE_API_URL" \
    --env "CVAT_INFERENCE_API_KEY=$CVAT_INFERENCE_API_KEY" \
    --env "CVAT_INFERENCE_MODEL_NAME=$CVAT_INFERENCE_MODEL_NAME" \
    --platform-config '{"attributes":{"network":"cvat_cvat"}}'

nuctl get function rfdetr-scoreboards --platform local
