## Stable Audio 2.0: Audio-to-Audio API

### Description

**Audio-to-Audio** transforms existing audio samples into new high-quality musical compositions. Unlike text-to-audio, this mode preserves structure and sonic texture from a base audio file and modifies it based on a guiding prompt. Use it to:
- Reimagine stems or samples into new styles
- Prototype remix or genre-transfer ideas
- Evolve original compositions with prompt direction

---

### Usage Conditions

- **Endpoint**: `POST https://api.stability.ai/v2beta/audio/stable-audio-2/audio-to-audio`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Request Format**: `multipart/form-data`
- **Audio Output**: Stereo 44.1kHz, up to 190s duration
- **Credit Cost**:
  - Formula: `9 + 0.06 × steps`
  - Default (50 steps): 12 credits
  - Max (100 steps): 15 credits

---

### Request Parameters

| Field           | Required | Type     | Description |
|-----------------|----------|----------|-------------|
| `prompt`        | ✅        | string   | Text-based instructions for transformation (max 10,000 chars) |
| `audio`         | ✅        | binary   | Source audio input (`mp3` or `wav`) |
| `duration`      | ❌        | number   | Output duration (1–190 seconds), default: 190 |
| `seed`          | ❌        | int      | Fixed randomness control |
| `steps`         | ❌        | int      | Sampling steps (30–100), default: 50 |
| `cfg_scale`     | ❌        | float    | Prompt adherence (1–25), default: 7 |
| `strength`      | ❌        | float    | Source audio influence (0–1), default: 1 |
| `output_format` | ❌        | enum     | `mp3` (default), `wav` |
| `negative_prompt` | ❌      | string   | Elements to exclude from final generation |
| `stability-client-id`, `stability-client-user-id`, `stability-client-version` | ❌ | string | Optional for diagnostics and analytics |

---

### Input Audio Constraints

- **Formats**: `mp3`, `wav`
- **Duration**: Must be between 6 and 190 seconds
- **Max size**: 50MB

---

### Usage Example (Python)

```python
import requests

response = requests.post(
    "https://api.stability.ai/v2beta/audio/stable-audio-2/audio-to-audio",
    headers={
        "authorization": "Bearer sk-MYAPIKEY",
        "accept": "audio/*"
    },
    files={
        "audio": open("./uk-bass-base.mp3", "rb"),
    },
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

- Do **not** upload copyrighted content.
- Choose `strength < 1.0` to better blend prompt and base audio.
- Results are constrained by length and input quality.
