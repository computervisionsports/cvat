import json
import os

import requests
import yaml

# The model reports one label per broadcaster ("scoreboard_sb_ESPN"). CVAT only
# auto-maps labels whose names match exactly, so they are collapsed into a
# single "scoreboard" label that carries the broadcaster as an attribute.
SCOREBOARD_LABEL_PREFIX = "scoreboard_sb_"
SCOREBOARD_LABEL = "scoreboard"
BROADCASTER_ATTRIBUTE = "broadcaster"


def init_context(context):
    """Initialize the reusable HTTP client and validate runtime configuration."""
    context.logger.info("Initializing CVAT inference API proxy")

    with open("/opt/nuclio/function.yaml", "rb") as function_file:
        fn_config = yaml.safe_load(function_file)

    labels_spec = fn_config["metadata"]["annotations"]["spec"]
    labels = json.loads(labels_spec)
    context.user_data.labels = {item["name"] for item in labels}
    context.user_data.broadcasters = {
        value
        for item in labels
        if item["name"] == SCOREBOARD_LABEL
        for attribute in item.get("attributes", [])
        if attribute["name"] == BROADCASTER_ATTRIBUTE
        for value in attribute["values"]
    }

    # The URL must include the endpoint, for example:
    # http://host.docker.internal:8000/v1/inference
    api_url = os.environ.get("CVAT_INFERENCE_API_URL")
    api_key = os.environ.get("CVAT_INFERENCE_API_KEY")
    model_name = os.environ.get(
        "CVAT_INFERENCE_MODEL_NAME",
        "rfdetr_inference_model",
    )

    missing = [
        name
        for name, value in (
            ("CVAT_INFERENCE_API_URL", api_url),
            ("CVAT_INFERENCE_API_KEY", api_key),
        )
        if not value
    ]
    if missing:
        raise RuntimeError("Missing required environment variables: {}".format(", ".join(missing)))

    context.user_data.api_url = api_url
    context.user_data.api_key = api_key
    context.user_data.model_name = model_name
    context.user_data.session = requests.Session()

    context.logger.info(f"Inference proxy ready: model={model_name} endpoint={api_url}")


def handler(context, event):
    """Forward a CVAT detector request to the FastAPI inference service."""
    data = event.body
    base64_image = data.get("image")

    if not base64_image:
        return _response(context, [], status_code=400)

    payload = {
        "api_key": context.user_data.api_key,
        "model_name": context.user_data.model_name,
        "encoded_image": base64_image,
        "threshold": float(data.get("threshold", 0.5)),
    }

    try:
        response = context.user_data.session.post(
            context.user_data.api_url,
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as exc:
        context.logger.error(f"Inference API request failed: {exc!s}")
        return _response(context, [], status_code=502)
    except ValueError as exc:
        context.logger.error(f"Inference API returned invalid JSON: {exc!s}")
        return _response(context, [], status_code=502)

    results = body.get("results")
    if not isinstance(results, list):
        context.logger.error("Inference API response does not contain a results list")
        return _response(context, [], status_code=502)

    results = [
        _collapse_scoreboard(item, context.user_data.broadcasters)
        for item in results
        if isinstance(item, dict)
    ]

    # CVAT can only map labels advertised by function.yaml. Dropping an unknown
    # label here also prevents backend configuration mistakes from creating
    # unusable annotations.
    unknown_labels = {
        item.get("label") for item in results if item.get("label") not in context.user_data.labels
    }
    if unknown_labels:
        context.logger.warning(
            f"Dropping results with labels not advertised by this function: {sorted(str(label) for label in unknown_labels)}"
        )

    valid_results = [item for item in results if item.get("label") in context.user_data.labels]
    return _response(context, valid_results, status_code=200)


def _collapse_scoreboard(item, allowed_broadcasters):
    """Turn a per-broadcaster scoreboard label into label plus attribute form."""
    label = item.get("label")
    if not isinstance(label, str) or not label.startswith(SCOREBOARD_LABEL_PREFIX):
        return item

    broadcaster = label[len(SCOREBOARD_LABEL_PREFIX) :]
    collapsed = dict(item, label=SCOREBOARD_LABEL)

    # CVAT drops attribute values that the task label does not declare, so only
    # broadcasters advertised in function.yaml are worth sending.
    if broadcaster in allowed_broadcasters:
        attributes = [
            attribute
            for attribute in collapsed.get("attributes", [])
            if isinstance(attribute, dict) and attribute.get("name") != BROADCASTER_ATTRIBUTE
        ]
        attributes.append({"name": BROADCASTER_ATTRIBUTE, "value": broadcaster})
        collapsed["attributes"] = attributes

    return collapsed


def _response(context, body, status_code):
    """Build the bare-array response expected by CVAT detector functions."""
    return context.Response(
        body=json.dumps(body),
        headers={},
        content_type="application/json",
        status_code=status_code,
    )
