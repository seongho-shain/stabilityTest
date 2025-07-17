## Stable Audio 2.0: Text-to-Audio API

### Description

**Stable Audio 2.0** generates stereo 44.1kHz high-quality music and sound effects up to 3 minutes long directly from descriptive text prompts. Use it to:
- Create audio for podcasts, games, or video backdrops
- Explore prompt-driven music composition
- Rapidly prototype sound designs

The model was trained exclusively on licensed data from AudioSparx, ensuring ethical and legal use.

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Audio Output**: Stereo, 44.1kHz, up to 190 seconds
- **Credit Cost**:
  - Base: 9 credits
  - Plus: `0.06 × steps`
  - Default (50 steps): 12 credits
  - Max (100 steps): 15 credits

---

### Request Parameters

| Field           | Required | Type     | Description |
|-----------------|----------|----------|-------------|
| `prompt`        | ✅        | string   | Descriptive audio instructions (max 10,000 chars) |
| `output_format` | ❌        | enum     | `mp3` (default), `wav` |
| `duration`      | ❌        | number   | Audio length in seconds (1–190), default: `190` |
| `seed`          | ❌        | int      | Random seed (0 = random) |
| `steps`         | ❌        | int      | Sampling steps (30–100), default: `50` |
| `cfg_scale`     | ❌        | float    | Prompt adherence (1–25), default: `7` |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional identifiers for debugging, tracking |

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "audio/*"
    },
    files={"none": ''},
    data={
        "prompt": "A song in the 3/4 time signature that features cheerful acoustic guitar, live recorded drums, and rhythmic claps. The mood is happy and up-lifting.",
        "output_format": "mp3",
        "duration": 20,
        "steps": 30,
    },
)

if response.status_code == 200:
    with open("./output.mp3", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- The prompt heavily influences instrument choice, rhythm, and genre.
- Audio longer than 190s or fewer than 30 steps is not supported.
- Ensure descriptive and coherent phrasing for best results.
