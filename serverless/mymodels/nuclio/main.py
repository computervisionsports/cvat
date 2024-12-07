import json
import base64
from PIL import Image
import io
import yaml
import os
import json
import requests
from urllib.parse import urljoin

FUNC_NAME = "tm_scoreboards"

def log(texto):
    with open(f'logging_{FUNC_NAME}.txt', 'a') as f:
        f.write(texto+"\n")

def persist_var_env(name, value):
    with open(name, 'w') as f:
        f.write(value)

def read_var_env_from_file(name):
    with open(name, 'r') as f:
        return f.readline().strip()
    return None


def init_context(context):
    context.logger.info("Init context...  0%")

    log("entrou na init_context")

    # Read labels
    with open("/opt/nuclio/function.yaml", 'rb') as function_file:
        fn_config = yaml.safe_load(function_file)

    # Get labels from function.yaml'
    labels_spec = fn_config['metadata']['annotations']['spec']
    context.user_data.labels = {item['id']: item['name'] for item in json.loads(labels_spec)}
    log(f"context.user_data.labels: {context.user_data.labels}")

    # Read TM_TARGET_CLASS from env var
    target_class = os.environ.get("TM_TARGET_CLASS", None)
    # Save TM_TARGET_CLASS into file
    persist_var_env("TM_TARGET_CLASS", target_class)
    # Set TM_TARGET_CLASS to context.user_data.target_class
    context.user_data.target_class = target_class
    log(f"target_class from var env: {context.user_data.target_class}")

    # Read INFERENCE_API_URI from env var
    context.user_data.inference_api_uri = os.environ.get("SAMBA_INFERENCE_URI", None)
    context.user_data.inference_api_uri = urljoin(context.user_data.inference_api_uri, FUNC_NAME)
    log(f"inference_api_uri from var env: {context.user_data.inference_api_uri}")

    # Read INFERENCE_API_KEY from env var
    context.user_data.inference_api_key = os.environ.get("SAMBA_API_KEY", None)
    log(f"inference_api_key from var env: {context.user_data.inference_api_key}")

    context.logger.info("Init context...100%")


# def handler(context, event):
#     log("Entered in handler")
#     # Read target class from file
#     context.user_data.target_class = read_var_env_from_file("TM_TARGET_CLASS")
#     log(f"target_class from file: {context.user_data.target_class}")
#     log(f"inference_api_uri: {context.user_data.inference_api_uri}")
#     log(f"inference_api_key: {context.user_data.inference_api_key}")
#     # PRONTO! AQUI CHAMO A API
#     results = []
#     for i in range(10):
#         results.append({
#                 "confidence": str(float(0.1*i)),
#                 "label": context.user_data.target_class,
#                 "points": (i, i, i+i, i+i),
#                 "type": "rectangle",
#             })
#     log("Leaving handler")
#     return context.Response(body=json.dumps(results), headers={},
#         content_type='application/json', status_code=200)

def handler(context, event):
    log("Entered in handler")

    # Read target class from file
    context.user_data.target_class = read_var_env_from_file("TM_TARGET_CLASS")
    log(f"target_class from file: {context.user_data.target_class}")
    log(f"inference_api_uri: {context.user_data.inference_api_uri}")
    log(f"inference_api_key: {context.user_data.inference_api_key}")

    # Decode the image from the event
    data = event.body
    base64_image = data.get("image", None)
    log(f"base64_image: {base64_image}")
    log(f"type(base64_image): {type(base64_image)}")

    if not base64_image:
        return context.Response(body=json.dumps([]), headers={},
        content_type='application/json', status_code=400)

    # buf = io.BytesIO(base64.b64decode(image))

    # Prepare the payload for the POST request
    payload = {
             "api_key": context.user_data.inference_api_key,
             "target_class": context.user_data.target_class,
             "encoded_image": base64_image
         }
    log(f"payload: {base64_image}")
    # Send the request
    response = requests.post(context.user_data.inference_api_uri, json=payload)
    if response.status_code != 200:
        return context.Response(body=json.dumps([]), headers={},
            content_type='application/json', status_code=400)

    result = response.json()
    log(f"response.status_code: {response.status_code}")
    log(f"response: {result}")
    log(f"results: {result.get('results',[])}")
    return context.Response(body=json.dumps(result.get('results',[])), headers={},
        content_type='application/json', status_code=200)

    # results = []
    # for i in range(10):
    #     results.append({
    #         "confidence": str(float(0.1*i)),
    #         "label": context.user_data.target_class,
    #         "points": (i, i, i+i, i+i),
    #         "type": "rectangle",
    #     })
    # return context.Response(body=json.dumps(results), headers={},
    #     content_type='application/json', status_code=200)

    # response.raise_for_status()  # Raise an error for bad responses

    # # Parse the JSON response
    # results = response.json()
    # log("Received results from API")

    # log("Leaving handler")

    # return context.Response(body=json.dumps(results), headers={},
    #     content_type='application/json', status_code=200)
    return context.Response(body=json.dumps([]), headers={},
            content_type='application/json', status_code=400)
