## Sketch ControlNet API

### Description

**Sketch** is Stability AI’s sketch-to-image API, designed to turn rough sketches into fully rendered, detailed images. It supports both hand-drawn sketches and structured edge maps, making it ideal for:
- Design iteration workflows
- Controlled image generation using contours
- Artistic transformation of concept sketches

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/control/sketch`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**: Matches resolution and aspect ratio of input image
- **Credit Cost**: 3 credits per successful generation

---

### Request Parameters

| Field            | Required | Type     | Description |
|------------------|----------|----------|-------------|
| `prompt`         | ✅        | string   | Text prompt describing the desired image (max 10,000 chars) |
| `image`          | ✅        | binary   | Input sketch image (`jpeg`, `png`, `webp`) |
| `control_strength`| ❌       | float    | Strength of guidance from image (default: `0.7`) |
| `negative_prompt`| ❌       | string   | Unwanted elements to suppress |
| `seed`           | ❌       | int      | Set random seed for deterministic output |
| `output_format`  | ❌       | enum     | `png` (default), `jpeg`, `webp` |
| `style_preset`   | ❌       | enum     | e.g. `digital-art`, `anime`, `pixel-art`, etc. |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional metadata for analytics and debugging |

---

### Image Constraints

- **Min dimension**: 64px
- **Max total pixels**: 9,437,184 (e.g. `3072x3072`)
- **Aspect ratio**: Between `1:2.5` and `2.5:1`

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/control/sketch",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={
        "image": open("./sketch.png", "rb")
    },
    data={
        "prompt": "a medieval castle on a hill",
        "control_strength": 0.7,
        "output_format": "webp"
    },
)

if response.status_code == 200:
    with open("./castle.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- Input image must be properly sized and formatted.
- `control_strength` too high may overfit to sketch lines, too low may ignore them.
- Prompt clarity is crucial to avoid unwanted features.
