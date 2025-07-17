## Style Guide ControlNet API

### Description

**Style Guide** extracts the visual style from an input image and applies it to a new image generated from a prompt. Ideal for:
- Maintaining stylistic consistency across scenes
- Style transfer from concept art or reference imagery
- Cinematic or art-directed asset generation

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/control/style`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**: Fixed at 1 megapixel (`1024x1024` default)
- **Credit Cost**: 4 credits per successful generation

---

### Request Parameters

| Field             | Required | Type     | Description |
|-------------------|----------|----------|-------------|
| `prompt`          | ✅        | string   | Text description for image content (max 10,000 chars) |
| `image`           | ✅        | binary   | Style reference image (`jpeg`, `png`, `webp`) |
| `negative_prompt` | ❌        | string   | What to exclude in the output |
| `aspect_ratio`    | ❌        | enum     | One of: `1:1` (default), `16:9`, `3:2`, etc. |
| `fidelity`        | ❌        | float    | Style adherence (0 to 1), default `0.5` |
| `seed`            | ❌        | int      | Randomness control (0 = random) |
| `output_format`   | ❌        | enum     | `png` (default), `jpeg`, `webp` |
| `style_preset`    | ❌        | enum     | e.g. `anime`, `digital-art`, `cinematic`, etc. |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional app/user metadata |

---

### Image Constraints

- **Min dimension**: 64px
- **Max pixels**: 9,437,184 (e.g., `3072x3072`)
- **Aspect ratio**: Between `1:2.5` and `2.5:1`

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/control/style",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={
        "image": open("./cinematic-portrait.png", "rb")
    },
    data={
        "prompt": "a majestic portrait of a chicken",
        "output_format": "webp"
    },
)

if response.status_code == 200:
    with open("./chicken-portrait.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- High `fidelity` values may reduce prompt influence.
- Prompt and reference image should conceptually align for best results.
- Aspect ratio only affects output framing, not resolution (still 1MP).
