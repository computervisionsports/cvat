# CVAT inference API proxies

These Nuclio functions are thin adapters:

```text
CVAT -> Nuclio function -> FastAPI /v1/inference -> ONNX model
```

Each function receives CVAT's base64 image, forwards it to the
`cvat_api_inference_models` service with a fixed `model_name`, and returns the
bare detector-result array CVAT expects.

| Function | Display name | API `model_name` | Project labels |
| --- | --- | --- | --- |
| `rfdetr-scoreboards` | RF-DETR Scoreboards and Parts | `scoreboard_general` | rectangles (see [Scoreboard labels](#scoreboard-labels)) |
| `yolo-tennis-court-keypoints` | YOLO Pose Tennis Court Keypoints | `tennis_court_keypoints` | skeleton `tennis_court` + `point_1`…`point_14` |

## 1. Start CVAT with serverless support

From the CVAT repository:

```bash
docker compose \
  -f docker-compose.yml \
  -f components/serverless/docker-compose.serverless.yml \
  up -d
```

Use the development compose file too if that is how your CVAT checkout is run.

## 2. Start the inference API

From `cvat_api_inference_models`:

```bash
uv sync --extra all
export CVAT_INFERENCE_API_KEY=dev-api-key-change-me
uv run cvat-inference
```

The API binds to `0.0.0.0:8000` by default. Check it from the host:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/models
```

Install `--extra rfdetr` or `--extra yolo` instead of `--extra all` if you only
need one backend.

## 3. Deploy the Nuclio proxies

From the CVAT repository:

```bash
export CVAT_INFERENCE_API_KEY=dev-api-key-change-me
# API in Docker on cvat_cvat: http://cvat_inference_api:8000/v1/inference
# API on host (uv run):       http://host.docker.internal:8000/v1/inference
export CVAT_INFERENCE_API_URL=http://cvat_inference_api:8000/v1/inference

./serverless/mymodels/deploy.sh
# or one function:  ./serverless/mymodels/deploy.sh scoreboards
#                   ./serverless/mymodels/deploy.sh tennis_court
```

`host.docker.internal` is available in Docker Desktop on macOS. On Linux,
either run the API as a container attached to the `cvat_cvat` network and use
its container name, or set `CVAT_INFERENCE_API_URL` to a host address reachable
from the Nuclio container.

The API key must be identical in the API process and Nuclio deployment.
Redeploy the function after changing any `CVAT_INFERENCE_*` value.

## 4. Use the models

1. Open CVAT's **Models** page and confirm the deployed functions appear.
2. Create project/task labels that match the function spec (names and types).
   For the tennis-court skeleton, the easiest path is **Constructor → From
   model** and picking **YOLO Pose Tennis Court Keypoints**. You can also paste
   [`tennis_court_project_labels.json`](tennis_court_project_labels.json) into
   the **Raw** tab.
3. In a job, open **AI Tools -> Detectors**, select the model, and annotate the
   current frame. For a whole task, use **Actions -> Automatic annotation**.

CVAT auto-maps labels whose names match exactly. Skeleton models also require
matching sublabel names (`point_1` … `point_14`) and type `skeleton` — a
rectangle or `any` label will not accept pose output.

## Scoreboard labels

The model emits one label per broadcaster (`scoreboard_sb_ESPN`,
`scoreboard_sb_FOX`, ...), but CVAT only auto-maps labels whose names match a
task label exactly, which would mean mapping each one by hand on every run.
The handler therefore rewrites them into a single `scoreboard` label with the
broadcaster carried in a `broadcaster` attribute:

```json
{ "label": "scoreboard", "attributes": [{ "name": "broadcaster", "value": "ESPN" }] }
```

For this to map itself, the task needs a label named `scoreboard` with a
`select` attribute named `broadcaster` whose values match those declared in
`function.yaml`. CVAT discards attribute values the task label does not list,
so the two sets must be kept in sync; adding a broadcaster means updating
`function.yaml` and the task label together.

## Tennis court labels

`tennis_court_keypoints` returns one skeleton named `tennis_court` with 14
`points` elements `point_1` … `point_14`. The Nuclio spec in
`nuclio/tennis_court.yaml` advertises that skeleton (including an SVG template)
so CVAT can list it on the Models page, copy it via **From model**, and keep
the pose results instead of dropping them as unknown labels.

You cannot change a skeleton definition after the project is created. If the
project was set up without this label, create a new project.

## Troubleshooting

```bash
nuctl get functions --platform local
docker logs nuclio
docker logs nuclio-nuclio-rfdetr-scoreboards
docker logs nuclio-nuclio-yolo-tennis-court-keypoints
```

From inside the Nuclio container/network, the FastAPI URL must be reachable.
An HTTP 502 from the function means the proxy could not call the API or the API
returned an invalid response. Check both the Nuclio logs and API logs.

To exercise the whole chain without CVAT, POST `{"image": "<base64>"}` to the
function's published port (`NODE PORT` in `nuctl get functions`). A successful
call returns a JSON array, which is empty when the model finds nothing.

### `No matching distribution found for msgpack`

Nuclio ends every Python build with an offline
`pip install nuclio-sdk msgpack --no-index`, but its `handler-builder-python-onbuild`
images ship x86_64 msgpack wheels for every architecture, so the build fails on
Apple Silicon and other arm64 hosts. `function.yaml` works around this by
downloading a matching wheel into `/opt/nuclio/whl` before that step. If a
future Nuclio release bundles correct wheels, the directive can be dropped.
