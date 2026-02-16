# Chaka AI Developer Documentation (v1.0)

Welcome to the **Chaka AI Platform**. You can now leverage Chaka's high-precision 4-phase logic audit in your own projects.

## API Endpoint
`POST http://localhost:5001/api/chat`

## Authentication
Every request must include the `X-Chaka-API-Key` header with a valid key.

| Header | Description |
| :--- | :--- |
| `X-Chaka-API-Key` | Your unique project key (e.g., `temple-project-alpha`) |

## Layered System Prompts
Chaka uses a **Foundation-First** architecture. 
1. **Base Logic**: Chaka's "Syntactic & Semantic Audit (V5)" is always executed first.
2. **Project Layer**: You can provide a `custom_prompt` in your request body to give the AI specific context or instructions for your project.

> [!NOTE]
> Your `custom_prompt` will be appended to Chaka's core rules, ensuring high logical precision while following your project's persona or data rules.

## JSON Request Body
```json
{
  "message": "User query here",
  "custom_prompt": "You are a historical research assistant for Temple.dev",
  "model": "llama-3.3-70b-versatile",
  "session_id": "optional-unique-session"
}
```

## JSON Response
```json
{
  "response": "The final answer",
  "thought": "The 4-phase logic audit monologue",
  "project": "Your Project Name"
}
```

## Implementation Examples

### Python (using requests)
```python
import requests

url = "http://localhost:5001/api/chat"
headers = {
    "X-Chaka-API-Key": "your-key-here",
    "Content-Type": "application/json"
}
payload = {
    "message": "Who marched into the tent?",
    "custom_prompt": "You are a precise librarian.",
    "model": "llama-3.3-70b-versatile"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print(f"Thought: {data['thought']}")
print(f"Answer: {data['response']}")
```

### Node.js (using fetch)
```javascript
const url = "http://localhost:5001/api/chat";
const payload = {
    message: "Who marched into the tent?",
    custom_prompt: "You are a precise librarian.",
    model: "llama-3.3-70b-versatile"
};

fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Chaka-API-Key': 'your-key-here'
    },
    body: JSON.stringify(payload)
})
.then(res => res.json())
.then(data => {
    console.log("Thought:", data.thought);
    console.log("Answer:", data.response);
});
```

## Getting Started
Contact the Chaka Admin to register your `X-Chaka-API-Key`. Currently Authorized:
- `chaka-internal-dev` (Admin)
- `temple-project-alpha` (External Example)
