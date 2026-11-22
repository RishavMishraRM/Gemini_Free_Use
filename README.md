# Web API — Free Gemini & ChatGPT

A unified **FastMCP Server** and **local Web2API proxy suite** that lets you use both **Google Gemini** and **OpenAI ChatGPT** 100% free with zero API keys and zero cost.

---

## Features

- **Both Gemini & ChatGPT included in the code**:
  - `gemini_web2api.py`: Converts Gemini's web stream into an OpenAI-compatible API on port `8081`.
  - `chatgpt_web2api.py`: Converts ChatGPT into an OpenAI-compatible API on port `8080`.
  - `gemini_mcp_server.py`: Unified MCP server with `ask_gemini`, `ask_chatgpt`, and `ask_ai`.
- **Zero API Keys Required**: Both providers work out of the box without paying for API credits.
- **Fail-safe Auto Fallback**: If `chatgpt_web2api.py` is not running on port `8080`, `ask_chatgpt` automatically falls back to the built-in free ChatGPT engine directly in Python.

---

## File Structure

```
Web_API/
├── gemini_mcp_server.py   # FastMCP Server (ask_gemini, ask_chatgpt, ask_ai)
├── gemini_web2api.py      # Local Gemini Web2API proxy server (port 8081)
├── chatgpt_web2api.py     # Local ChatGPT Web2API proxy server (port 8080)
├── config.json            # Proxy server settings & local API keys
├── main.py                # Test runner & alternative MCP server launcher
├── litellm.yaml           # LiteLLM routing config for both models
├── requirements.txt       # Dependencies (httpx, mcp, g4f)
└── pyproject.toml         # Project metadata
```

---

## Setup After Cloning

### 1. Create and Activate Virtual Environment

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

Using `pip` or `uv`:
```powershell
pip install -r requirements.txt
```
*(Or with uv: `uv pip install -r requirements.txt`)*

---

## How to Test Both Gemini & ChatGPT

### Run the Demo Test Script
Run `main.py` directly to test both models:
```powershell
python main.py
```

Output:
```
==================================================
      Testing Web API (Gemini & ChatGPT - FREE)   
==================================================

[1] Testing Gemini (via gemini_web2api.py on :8081)...
Gemini: I am Gemini, a large language model built by Google.

[2] Testing ChatGPT (FREE via chatgpt_web2api / built-in engine)...
ChatGPT: I'm ChatGPT, developed by OpenAI.

[3] Testing ask_ai unified tool...
ask_ai(gemini):  I am Gemini...
ask_ai(chatgpt): I'm ChatGPT...

All tests completed!
```

---

## How to Run

### Option A: Run the Proxies + MCP Server

1. **Terminal 1: Start Gemini Proxy**
   ```powershell
   python gemini_web2api.py
   ```
   *Runs at `http://127.0.0.1:8081/v1`*

2. **Terminal 2: Start ChatGPT Proxy**
   ```powershell
   python chatgpt_web2api.py
   ```
   *Runs at `http://127.0.0.1:8080/v1`*

3. **Terminal 3: Start the FastMCP Server**
   ```powershell
   python gemini_mcp_server.py
   ```
   *(Or `python main.py server`)*

---

## Testing with curl

### Test Gemini
```powershell
curl.exe --% http://127.0.0.1:8081/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-gemini-local" -d "{\"model\":\"gemini-3.6-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}"
```

### Test ChatGPT
```powershell
curl.exe --% http://127.0.0.1:8080/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-chatgpt-local" -d "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}"
```

---

## Testing with OpenAI Python SDK

Any app that supports OpenAI API can connect to your local servers:

```python
from openai import OpenAI

# 1. Gemini (FREE via local proxy)
gemini = OpenAI(base_url="http://127.0.0.1:8081/v1", api_key="sk-gemini-local")
resp = gemini.chat.completions.create(
    model="gemini-3.6-flash",
    messages=[{"role": "user", "content": "What is quantum computing in one sentence?"}]
)
print("Gemini:", resp.choices[0].message.content)

# 2. ChatGPT (FREE via local proxy)
chatgpt = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="sk-chatgpt-local")
resp = chatgpt.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is quantum computing in one sentence?"}]
)
print("ChatGPT:", resp.choices[0].message.content)
```

---

## MCP Tools Reference

When connecting this server to Claude Desktop, Cursor, Antigravity, or other MCP clients:

| Tool | Default Model | Description |
|---|---|---|
| `ask_gemini` | `gemini-3.6-flash` | Queries Google Gemini via `gemini_web2api.py` |
| `ask_chatgpt` | `gpt-4o-mini` | Queries OpenAI ChatGPT via `chatgpt_web2api.py` or direct fallback |
| `ask_ai` | depends on provider | Unified tool — select `provider="gemini"` or `provider="chatgpt"` |

All tools accept parameters:
- `prompt` (required): The user question or instructions.
- `model` (optional): Model identifier override.
- `system_prompt` (optional): System instruction message.

---

## Available Models

### Gemini Models
- `gemini-3.6-flash` (Default, fast, all-around)
- `gemini-3.5-flash-thinking` (Deep thinking mode)
- `gemini-auto` (Auto selection)
- `gemini-flash-lite` (Lightweight and fast)
- `gemini-3.1-pro` (Requires optional Google cookie in `config.json`)

### ChatGPT Models
- `gpt-4o-mini` (Default, fast and reliable)
- `gpt-4o` (Full GPT-4o model)
- `auto` (Auto model selection)

---

## LiteLLM Unified Proxy (Optional)

If you want a single unified endpoint routing both models on port `4000`:
```powershell
pip install litellm[proxy]
litellm --config litellm.yaml --port 4000
```
- Routes `gemini-*` to `127.0.0.1:8081` (FREE)
- Routes `gpt-*` to `127.0.0.1:8080` (FREE)
