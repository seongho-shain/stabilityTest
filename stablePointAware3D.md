## Stable Point Aware 3D (SPAR3D) API

### Description

**Stable Point Aware 3D (SPAR3D)** generates complete 3D models from a single 2D image using a hybrid technique combining point cloud diffusion and mesh regression. It allows:
- Richer backside and depth reconstruction
- Real-time editing of occluded geometry
- Higher-fidelity geometry compared to Stable Fast 3D

SPAR3D is ideal for detailed asset creation in 3D production pipelines or virtual scenes.

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/3d/stable-point-aware-3d`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Output Format**: Binary `.glb` file (gLTF + buffers, images)
- **Credit Cost**: 4 credits per successful generation

---

### Request Parameters

| Field             | Required | Type     | Description |
|-------------------|----------|----------|-------------|
| `image`           | ✅        | binary   | Input image file (`jpeg`, `png`, `webp`) |
| `texture_resolution`| ❌      | enum     | Texture detail: `512`, `1024` (default), `2048` |
| `foreground_ratio` | ❌      | float    | Object size within frame (1–2), default `1.3` |
| `remesh`           | ❌      | enum     | `none` (default), `quad`, `triangle` |
| `target_type`      | ❌      | enum     | Mesh simplification mode: `none`, `vertex`, `face` |
| `target_count`     | ❌      | number   | Number of vertices/faces (100–20,000), default `1000` |
| `guidance_scale`   | ❌      | float    | Point diffusion guidance (1–10), default `3` |
| `seed`             | ❌      | number   | Random seed (0 = random) |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional for app tracking/debugging |

---

### Input Image Constraints

- **Min size**: 64px per side
- **Max pixels**: 4,194,304 (e.g. 2048x2048)
- **Aspect ratio**: Flexible within resolution limits

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/3d/stable-point-aware-3d",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
    },
    files={
        "image": open("./cat-statue.png", "rb")
    },
    data={},
)

if response.status_code == 200:
    with open("./3d-cat-statue.glb", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- Higher `guidance_scale` may introduce artifacts; default is recommended.
- For best use in Maya or Blender, set `remesh` to `quad`.
- Setting `target_count` too low (< 500) reduces fidelity significantly.
