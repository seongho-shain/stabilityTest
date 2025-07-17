## Fetch Async Generation Result API

### Description

Use this endpoint to retrieve the result of an asynchronous generation by its ID. Results are stored for 24 hours after completion and are accessible only with the same API key used to initiate the generation.

---

### Usage Conditions

- **Endpoint**: `GET https://api.stability.ai/v2beta/results/{generation_id}`
- **Authentication**: API Key in `Authorization` header (`Bearer <your-key>`)
- **Path Parameter**:
  - `generation_id`: A 64-character ID of the generation
- **Response Handling**:
  - `202 Accepted`: Generation still in progress
  - `200 OK`: Generation completed successfully
  - `404 Not Found`: Invalid or expired generation ID, or mismatched API key
- **Storage Duration**: Results are retained for 24 hours

---

### Request Parameters

| Parameter                 | Location | Required | Type    | Description |
|---------------------------|----------|----------|---------|-------------|
| `id`                      | Path     | ✅        | string  | ID of the generation (64-char hash) |
| `authorization`           | Header   | ✅        | string  | `Bearer <your-key>` |
| `accept`                  | Header   | ❌        | string  | `image/*` (default) or `application/json` for base64 |
| `stability-client-id`     | Header   | ❌        | string  | App name (e.g., `my-app`) |
| `stability-client-user-id`| Header   | ❌        | string  | Unique user ID (e.g., `User#0001`) |
| `stability-client-version`| Header   | ❌        | string  | App version (e.g., `1.0.0`) |

---

### Usage Example (Python)

```python
import requests

generation_id = "e52772ac75b..."  # Replace with actual ID

response = requests.get(
    f"https://api.stability.ai/v2beta/results/{generation_id}",
    headers={
        "accept": "image/*",  # Use 'application/json' for base64
        "authorization": "Bearer sk-MYAPIKEY"
    },
)

if response.status_code == 202:
    print("Generation in-progress, try again in 10 seconds.")
elif response.status_code == 200:
    print("Generation complete!")
    with open("result.webp", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(response.json())
```

---

### Warnings

- Use the **same API key** to fetch results as you did for generation.
- The result is **deleted after 24 hours**.
- If you receive `404`, the ID may be expired or invalid.
