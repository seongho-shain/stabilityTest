## Stable Image Core API

### Description

**Stable Image Core** is the high-speed, general-purpose text-to-image generation API from Stability AI. It offers fast generation with excellent quality and requires no advanced prompt engineering.

Best for:
- Character, object, or scene prompts
- Rapid image generation at scale

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/generate/core`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**:
  - Default resolution: ~1.5MP (e.g., 1152x1344 or similar depending on aspect)
  - Format: `image/*` (binary) or `application/json` (base64)
- **Cost**: 3 credits per successful result

---

### Request Parameters

| Field               | Required | Type    | Description |
|--------------------|----------|---------|-------------|
| `prompt`           | ✅       | string  | Descriptive text input (max 10,000 chars) |
| `aspect_ratio`     | ❌       | enum    | One of: 16:9, 1:1 (default), 2:3, 3:2, etc. |
| `negative_prompt`  | ❌       | string  | Elements to avoid in output |
| `seed`             | ❌       | int     | 0 for random seed or fixed integer |
| `style_preset`     | ❌       | enum    | e.g. `photographic`, `anime`, `3d-model`, etc. |
| `output_format`    | ❌       | enum    | `png` (default), `jpeg`, `webp` |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional metadata for debugging and moderation |

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/core",
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

- A `prompt` is always required.
- `output_format` and `aspect_ratio` are optional but recommended for better control.
- You will only be charged for successful generations.
