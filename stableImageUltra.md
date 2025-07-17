## Stable Image Ultra API

### Description

**Stable Image Ultra** is Stability AI's most advanced text-to-image generation service, built on top of Stable Diffusion 3.5. It delivers exceptional image quality, especially in areas like:
- Typography
- Dynamic lighting
- Color vibrancy
- Complex composition

The service accepts text prompts and optionally reference images, returning 1-megapixel images by default.

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/generate/ultra`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**:
  - Default: `1024x1024` resolution
  - Format: `image/*` (raw image) or `application/json` (base64-encoded image)
- **Cost**: 8 credits per successful result (free if failed)

---

### Request Parameters

| Field               | Required | Type    | Description |
|--------------------|----------|---------|-------------|
| `prompt`           | ✅       | string  | Main text input (max 10,000 chars) |
| `image`            | ❌       | binary  | Optional reference image (required if `strength` is used) |
| `strength`         | ❌       | float   | 0.0–1.0 control of image influence |
| `negative_prompt`  | ❌       | string  | Things to avoid in output |
| `aspect_ratio`     | ❌       | enum    | One of: 16:9, 1:1 (default), 2:3, 3:2, etc. |
| `seed`             | ❌       | int     | Random seed (0 = random) |
| `output_format`    | ❌       | enum    | `png` (default), `jpeg`, `webp` |
| `style_preset`     | ❌       | enum    | e.g. `photographic`, `anime`, `3d-model`, etc. |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional for debugging/analytics |

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/ultra",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "Lighthouse on a cliff overlooking the ocean",
        "output_format": "webp",
    },
)

if response.status_code == 200:
    with open("./lighthouse.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- You **must** provide the `strength` parameter if using an input `image`.
- Output is **always** 1MP regardless of aspect ratio.
- For exact parameter behavior, refer to official request schema.
- Overuse of vague prompts (e.g. "beautiful scene") may reduce output quality.
