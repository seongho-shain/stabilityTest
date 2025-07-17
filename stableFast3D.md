## Stable Fast 3D API

### Description

**Stable Fast 3D** generates realistic 3D assets in `.glb` format from a single 2D input image. The service creates detailed models with textures and normal maps, ideal for real-time applications, games, and 3D previews.

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/3d/stable-fast-3d`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Output Format**: Binary `.glb` file (gLTF with buffers + images)
- **Credit Cost**: 2 credits per successful generation

---

### Request Parameters

| Field               | Required | Type     | Description |
|---------------------|----------|----------|-------------|
| `image`             | ✅        | binary   | Input 2D image (`jpeg`, `png`, `webp`) |
| `texture_resolution`| ❌        | enum     | Texture detail: `512`, `1024` (default), `2048` |
| `foreground_ratio`  | ❌        | float    | Object framing control (0.1–1.0), default `0.85` |
| `remesh`            | ❌        | enum     | `none` (default), `quad`, `triangle` |
| `vertex_count`      | ❌        | number   | Target vertex count (default: `-1` for unlimited) |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional debugging metadata |

---

### Input Image Constraints

- **Min size**: 64px per side
- **Max pixels**: 4,194,304 (e.g. 2048x2048)
- **Aspect ratio**: Flexible within limits

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/3d/stable-fast-3d",
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

- Larger `texture_resolution` increases detail but also file size.
- `remesh=quad` is recommended for export to DCC tools like Maya or Blender.
- `vertex_count` allows for mesh simplification when needed.
