## Style Transfer API

### Description

**Style Transfer** applies the visual characteristics of a reference style image to a target input image while preserving its core composition. It differs from **Style Guide**, which uses the reference style as a prompt influence. Style Transfer is optimal for:
- Consistent visual styling across assets
- Retaining spatial layouts while applying new looks
- Transforming illustrations, concept art, or photos with custom styles

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/stable-image/control/style-transfer`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Image Output**: 1 megapixel resolution, same aspect ratio as `init_image`
- **Credit Cost**: 8 credits per successful generation

---

### Request Parameters

| Field                  | Required | Type     | Description |
|------------------------|----------|----------|-------------|
| `init_image`           | ✅        | binary   | Image to restyle (`jpeg`, `png`, `webp`) |
| `style_image`          | ✅        | binary   | Reference image for style (`jpeg`, `png`, `webp`) |
| `prompt`               | ❌        | string   | Description of desired result (max 10,000 chars) |
| `negative_prompt`      | ❌        | string   | Features to avoid in the output |
| `style_strength`       | ❌        | float    | Degree of style application (0–1), default `1.0` |
| `composition_fidelity` | ❌        | float    | Preserve structure of original image (default `0.9`) |
| `change_strength`      | ❌        | float    | How much to change the input image (0.1–1), default `0.9` |
| `seed`                 | ❌        | int      | Random seed for reproducibility |
| `output_format`        | ❌        | enum     | `png` (default), `jpeg`, `webp` |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional for app-specific tracking |

---

### Image Constraints

- **Dimensions**: Minimum 64x64, maximum 16,383x16,383 pixels
- **Aspect ratio**: Must be between `1:2.5` and `2.5:1`
- **Total pixel count**: Between 4,096 and 9,437,184 pixels

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/control/style-transfer",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "image/*"
    },
    files={
        "init_image": open("./chicken-portrait.png", "rb"),
        "style_image": open("./glowbot.png", "rb")
    },
    data={
        "output_format": "webp"
    },
)

if response.status_code == 200:
    with open("./glow-chicken.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- `init_image` and `style_image` must both be valid and well-formed images.
- Excessive `style_strength` or `change_strength` may erase original composition.
- Seed and fidelity settings affect repeatability and visual consistency.
