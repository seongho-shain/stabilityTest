## Structure ControlNet API

### Description

**Structure** is a control image generation API that preserves the structural layout of the input image. It is ideal for applications like:
- Scene recreation
- Stylized object or character rendering
- Model-based asset generation

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/control/structure`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**: Matches resolution and aspect ratio of input image
- **Credit Cost**: 3 credits per successful generation

---

### Request Parameters

| Field             | Required | Type     | Description |
|-------------------|----------|----------|-------------|
| `prompt`          | ✅        | string   | Description of the desired output image (max 10,000 chars) |
| `image`           | ✅        | binary   | Structural reference image (`jpeg`, `png`, `webp`) |
| `control_strength`| ❌        | float    | Influence of structure (default: `0.7`) |
| `negative_prompt` | ❌        | string   | Elements to suppress in output |
| `seed`            | ❌        | int      | Controls randomness (0 = random) |
| `output_format`   | ❌        | enum     | `png` (default), `jpeg`, `webp` |
| `style_preset`    | ❌        | enum     | e.g. `photographic`, `anime`, `digital-art`, etc. |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional metadata for debugging or analytics |

---

### Image Constraints

- **Min dimension**: 64px
- **Max pixels**: 9,437,184 (e.g., `3072x3072`)
- **Aspect ratio**: Must be between `1:2.5` and `2.5:1`

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/control/structure",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={
        "image": open("./cat-statue.png", "rb")
    },
    data={
        "prompt": "a well manicured shrub in an english garden",
        "control_strength": 0.7,
        "output_format": "webp"
    },
)

if response.status_code == 200:
    with open("./shrub-in-a-garden.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- Input image resolution must be within limits and not overly wide or tall.
- Overuse of `control_strength` may reduce creativity.
- Ensure prompt complements the input image structure for best results.
