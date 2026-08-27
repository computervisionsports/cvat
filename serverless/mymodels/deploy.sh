#!/usr/bin/env bash
#
# Deploy Nuclio proxies that connect CVAT to cvat-inference.
#
# Usage:
#   ./serverless/mymodels/deploy.sh              # both functions
#   ./serverless/mymodels/deploy.sh scoreboards
#   ./serverless/mymodels/deploy.sh tennis_court
#
# Required:
#   CVAT_INFERENCE_API_KEY
#
# Optional:
#   CVAT_INFERENCE_API_URL  default: http://host.docker.internal:8000/v1/inference
#   When the API runs in Docker on the cvat_cvat network (see cvat_api_inference_models
#   docker-compose.yml), use http://cvat_inference_api:8000/v1/inference instead.
#
# Each function is staged into its own directory so the image contains only
# that function.yaml. main.py reads /opt/nuclio/function.yaml for the label spec.
#
# On Linux, host.docker.internal may not resolve. Run the API in a container on
# the cvat_cvat network, or set CVAT_INFERENCE_API_URL to an address reachable
# from Docker.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
FUNCTION_DIR="$SCRIPT_DIR/nuclio"

: "${CVAT_INFERENCE_API_KEY:?Set CVAT_INFERENCE_API_KEY before deploying}"

CVAT_INFERENCE_API_URL="${CVAT_INFERENCE_API_URL:-http://host.docker.internal:8000/v1/inference}"

TARGET="${1:-all}"
case "$TARGET" in
    all|scoreboards|tennis_court) ;;
    *)
        echo "Usage: $0 [all|scoreboards|tennis_court]" >&2
        exit 1
        ;;
esac

# Project creation fails when it already exists; that is safe to ignore.
nuctl create project cvat --platform local 2>/dev/null || true

deploy_proxy() {
    local config_file="$1"
    local model_name="$2"
    local function_name="$3"
    local staging

    staging="$(mktemp -d "${TMPDIR:-/tmp}/cvat-mymodels.XXXXXX")"
    cp "$FUNCTION_DIR/main.py" "$staging/main.py"
    cp "$config_file" "$staging/function.yaml"

    nuctl deploy \
        --project-name cvat \
        --path "$staging" \
        --file "$staging/function.yaml" \
        --platform local \
        --env "CVAT_INFERENCE_API_URL=$CVAT_INFERENCE_API_URL" \
        --env "CVAT_INFERENCE_API_KEY=$CVAT_INFERENCE_API_KEY" \
        --env "CVAT_INFERENCE_MODEL_NAME=$model_name" \
        --platform-config '{"attributes":{"network":"cvat_cvat"}}'

    rm -rf "$staging"
    nuctl get function "$function_name" --platform local
}

if [[ "$TARGET" == "all" || "$TARGET" == "scoreboards" ]]; then
    deploy_proxy \
        "$FUNCTION_DIR/function.yaml" \
        "scoreboard_general" \
        "rfdetr-scoreboards"
fi

if [[ "$TARGET" == "all" || "$TARGET" == "tennis_court" ]]; then
    deploy_proxy \
        "$FUNCTION_DIR/tennis_court.yaml" \
        "tennis_court_keypoints" \
        "yolo-tennis-court-keypoints"
fi
