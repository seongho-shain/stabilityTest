## Stable Diffusion 3.5 API

### Description

**Stable Diffusion 3.5** is the latest generation of Stability AI's base models, offering advanced prompt adherence and image quality across multiple model sizes:

- **SD3.5 Large** (8B parameters): Professional-quality 1MP images.
- **SD3.5 Large Turbo**: Fast, 4-step image generation with near-identical quality.
- **SD3.5 Medium** (2.5B parameters): Fast, high-quality generation with optimal performance.

> All SD 3.0 API calls are automatically rerouted to SD 3.5 as of April 17, 2025.

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/generate/sd3`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**:
  - Default resolution: `1024x1024` (1MP)
  - Format: `image/*` or `application/json`
- **Cost**:
  - SD3.5 Large: 6.5 credits
  - SD3.5 Large Turbo: 4 credits
  - SD3.5 Medium: 3.5 credits

---

### Request Parameters

| Field            | Required | Type     | Description |
|------------------|----------|----------|-------------|
| `prompt`         | ✅        | string   | Description of desired image (max 10,000 chars) |
| `mode`           | ❌        | enum     | `text-to-image` (default) or `image-to-image` |
| `image`          | ❌        | binary   | Input image (required for `image-to-image`) |
| `strength`       | ❌        | float    | Degree of transformation (required for `image-to-image`) |
| `aspect_ratio`   | ❌        | enum     | One of: 1:1 (default), 16:9, 3:2, etc. Only for `text-to-image` |
| `model`          | ❌        | enum     | `sd3.5-large` (default), `sd3.5-large-turbo`, `sd3.5-medium` |
| `output_format`  | ❌        | enum     | `png` (default), `jpeg` |
| `seed`           | ❌        | int      | Fixed or random generation seed |
| `cfg_scale`      | ❌        | float    | Adherence to prompt (1–10). Default: 4 (Large/Medium), 1 (Turbo) |
| `negative_prompt`| ❌        | string   | Elements to exclude from output |
| `style_preset`   | ❌        | enum     | e.g. `anime`, `photographic`, `pixel-art`, etc. |

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "Lighthouse on a cliff overlooking the ocean",
        "output_format": "jpeg",
    },
)

if response.status_code == 200:
    with open("./lighthouse.jpeg", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- `image`, `strength`, and `mode=image-to-image` are required together.
- `aspect_ratio` is only valid for `text-to-image` mode.
- Total request size must be ≤ 10MiB.
- All model variants generate 1MP images regardless of aspect ratio.
