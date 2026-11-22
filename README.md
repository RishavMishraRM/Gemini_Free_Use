# Web API — Gemini & ChatGPT Unified Server

A unified **FastMCP server** and **LiteLLM proxy config** that lets you query both **Google Gemini** (free, via cookie-based `gemini-web2api`) and **OpenAI ChatGPT** (via official API or any OpenAI-compatible proxy) through a single interface.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup After Cloning](#setup-after-cloning)
- [Configuration](#configuration)
  - [Gemini (Free — via gemini-web2api)](#gemini-free--via-gemini-web2api)
  - [ChatGPT / OpenAI (Paid — API Key)](#chatgpt--openai-paid--api-key)
  - [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
  - [Step 1: Start the Gemini Web2API Proxy](#step-1-start-the-gemini-web2api-proxy)
  - [Step 2: Start the MCP Server](#step-2-start-the-mcp-server)
- [Testing](#testing)
  - [Run the Demo Script](#run-the-demo-script)
  - [Test Gemini with curl](#test-gemini-with-curl)
  - [Test ChatGPT with curl](#test-chatgpt-with-curl)
  - [Test with Python (OpenAI SDK)](#test-with-python-openai-sdk)
- [LiteLLM Proxy (Optional)](#litellm-proxy-optional)
- [MCP Tools Reference](#mcp-tools-reference)
- [Available Gemini Models](#available-gemini-models)
- [Troubleshooting](#troubleshooting)

---

## How It Works

```
┌──────────────────────────────────────────────────────┐
│                   Your App / Client                  │
│          (MCP client, curl, OpenAI SDK, etc.)        │
└───────────┬─────────────────────────┬────────────────┘
            │                         │
     ask_gemini()               ask_chatgpt()
     ask_ai(provider="gemini")  ask_ai(provider="chatgpt")
            │                         │
            ▼                         ▼
┌───────────────────────┐  ┌──────────────────────────┐
│  gemini-web2api       │  │  OpenAI API / Compatible  │
│  (local proxy)        │  │  Proxy                    │
│  http://127.0.0.1:8081│  │  https://api.openai.com   │
└───────────┬───────────┘  └──────────────────────────┘
            │
            ▼
┌───────────────────────┐
│  gemini.google.com    │
│  (Gemini Web UI)      │
│  FREE, no API key     │
└───────────────────────┘
```

- **Gemini** is completely free — `gemini-web2api` scrapes Gemini's web interface and exposes it as an OpenAI-compatible API. No Google API key needed.
- **ChatGPT** uses the official OpenAI API (requires an API key), or any OpenAI-compatible endpoint you configure.

---

## Project Structure

```
Web_API/
├── gemini_mcp_server.py      # FastMCP server — 3 tools: ask_gemini, ask_chatgpt, ask_ai
├── main.py                   # Demo/test runner + alternative MCP server launcher
├── requirements.txt          # Python dependencies (httpx, mcp)
├── pyproject.toml            # Project metadata
├── litellm-gemini.yaml       # LiteLLM config: Gemini + ChatGPT model routing
├── litellm-test.yaml         # LiteLLM config: Gemini-only test setup
├── gemini-web2api/           # Git submodule/folder — the local Gemini proxy
│   ├── gemini_web2api.py     # Standalone single-file server (alternative)
│   ├── gemini_web2api/       # Modular package version
│   │   ├── __main__.py       # python -m gemini_web2api entry point
│   │   ├── server.py         # HTTP handler (OpenAI + Google API compat)
│   │   ├── gemini.py         # Core Gemini protocol (StreamGenerate)
│   │   ├── models.py         # Model definitions & resolver
│   │   ├── config.py         # Config loader
│   │   ├── tools.py          # Prompt conversion & tool call parsing
│   │   └── multimodal.py     # Image upload support
│   ├── config.json           # Gemini proxy config (port, keys, etc.)
│   ├── config.example.json   # Example config (reference)
│   └── requirements.txt      # gemini-web2api's own deps (httpx)
└── .venv/                    # Python virtual environment (gitignored)
```

---

## Prerequisites

- **Python 3.13+** (see `.python-version`)
- **pip** or **uv** for package management
- **For ChatGPT**: An OpenAI API key (get one at https://platform.openai.com/api-keys)
- **For Gemini**: Nothing extra! `gemini-web2api` works without any API key by default

---

## Setup After Cloning

```powershell
# 1. Clone the repo
git clone <your-repo-url> Web_API
cd Web_API

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# PowerShell:
.\.venv\Scripts\Activate.ps1
# CMD:
.\.venv\Scripts\activate.bat
# Linux/macOS:
# source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install gemini-web2api's dependencies
pip install -r gemini-web2api/requirements.txt

# 6. (Optional) Set your OpenAI key for ChatGPT support
$env:OPENAI_API_KEY = "sk-your-openai-key-here"
# Or on Linux/macOS:
# export OPENAI_API_KEY="sk-your-openai-key-here"
```

> **Tip**: If you use `uv`, you can replace steps 2-5 with `uv sync` and `uv pip install -r gemini-web2api/requirements.txt`.

---

## Configuration

### Gemini (Free — via gemini-web2api)

The Gemini proxy is configured in `gemini-web2api/config.json`:

```json
{
  "port": 8081,
  "host": "127.0.0.1",
  "default_model": "gemini-3.6-flash",
  "api_keys": ["sk-gemini-local"],
  "cookie_file": null,
  "proxy": null,
  "log_requests": true,
  "temporary_chats": false
}
```

| Field | Description |
|---|---|
| `port` | Port for the proxy (default `8081`) |
| `api_keys` | Keys clients must send as `Bearer` token. Empty array = no auth |
| `cookie_file` | Path to a Google cookie file (needed for `gemini-3.1-pro`). Not required for Flash models |
| `proxy` | HTTP proxy URL if you need one (e.g., `http://127.0.0.1:7890`) |
| `temporary_chats` | If `true`, chats won't be saved to your Gemini history |

**Key point**: Flash models (`gemini-3.6-flash`, `gemini-3.5-flash-thinking`, etc.) work **without any cookie or login**. Pro models require a cookie from your logged-in Gemini session.

### ChatGPT / OpenAI (Paid — API Key)

ChatGPT is configured via environment variables. No config file needed.

You need an OpenAI API key — set it before running:

```powershell
$env:OPENAI_API_KEY = "sk-proj-..."
```

If you want to use a **custom OpenAI-compatible endpoint** (e.g., your own reverse proxy), set:

```powershell
$env:CHATGPT_BASE_URL = "http://your-proxy:8080/v1"
$env:CHATGPT_API_KEY = "your-custom-key"
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_BASE_URL` | `http://127.0.0.1:8081/v1` | URL for the gemini-web2api proxy |
| `GEMINI_API_KEY` | `sk-gemini-local` | Must match an entry in gemini-web2api's `config.json` → `api_keys` |
| `CHATGPT_BASE_URL` | Falls back to `OPENAI_BASE_URL`, then `https://api.openai.com/v1` | Base URL for ChatGPT |
| `CHATGPT_API_KEY` | Falls back to `OPENAI_API_KEY`, then empty | OpenAI API key |

---

## Running the Project

You need **two terminals** (one for the Gemini proxy, one for the MCP server).

### Step 1: Start the Gemini Web2API Proxy

This is the local proxy that converts Gemini's web interface into an OpenAI-compatible API.

```powershell
cd gemini-web2api
python gemini_web2api.py
```

You should see:
```
gemini-web2api v1.1.0
  Listening: http://0.0.0.0:8081
  Base URL:  http://localhost:8081/v1
  Models:    gemini-3.7-flash, gemini-3.6-flash, gemini-3.5-flash, ...
  Cookie:    none (anonymous)
```

> **Alternative**: You can also run the modular version: `python -m gemini_web2api`

**Leave this terminal running.**

### Step 2: Start the MCP Server

In a **second terminal**, start the FastMCP server:

```powershell
cd Web_API
.\.venv\Scripts\Activate.ps1
python gemini_mcp_server.py
```

This starts the MCP server with three tools: `ask_gemini`, `ask_chatgpt`, and `ask_ai`.

> **Alternative**: `python main.py server` does the same thing.

---

## Testing

### Run the Demo Script

The quickest way to verify everything works:

```powershell
# Make sure gemini-web2api is running in another terminal first!
python main.py
```

Output:
```
=== Web API Demo: Gemini & ChatGPT ===

[1] Testing Gemini (via Web2API)...
Gemini: I am Gemini, a large language model created by Google.

[2] Testing ChatGPT...
Note: OPENAI_API_KEY or CHATGPT_API_KEY is not set. Set it to query ChatGPT.
ChatGPT: Error communicating with ChatGPT: ...
```

If you see a Gemini response, Gemini is working. Set `OPENAI_API_KEY` to test ChatGPT too.

### Test Gemini with curl

```powershell
# PowerShell
curl.exe --% http://127.0.0.1:8081/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-gemini-local" -d "{\"model\":\"gemini-3.6-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello! What model are you?\"}]}"
```

```bash
# bash / macOS / Linux
curl http://127.0.0.1:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-gemini-local" \
  -d '{"model":"gemini-3.6-flash","messages":[{"role":"user","content":"Hello! What model are you?"}]}'
```

### Test ChatGPT with curl

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello! What model are you?"}]}'
```

### Test with Python (OpenAI SDK)

```python
from openai import OpenAI

# Test Gemini (via local proxy)
gemini = OpenAI(base_url="http://localhost:8081/v1", api_key="sk-gemini-local")
resp = gemini.chat.completions.create(
    model="gemini-3.6-flash",
    messages=[{"role": "user", "content": "What model are you?"}]
)
print("Gemini:", resp.choices[0].message.content)

# Test ChatGPT (direct to OpenAI)
chatgpt = OpenAI()  # uses OPENAI_API_KEY env var
resp = chatgpt.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What model are you?"}]
)
print("ChatGPT:", resp.choices[0].message.content)
```

---

## LiteLLM Proxy (Optional)

If you want to route all your model requests through a **single endpoint** (useful for apps that only support one API base URL), use LiteLLM as a unified proxy:

```powershell
pip install litellm[proxy]

# Start with the combined config (both Gemini and ChatGPT models):
litellm --config litellm-gemini.yaml --port 4000
```

This gives you `http://localhost:4000` as a single endpoint that routes:
- `gemini-3.6-flash`, `gemini-3.5-flash-thinking` → gemini-web2api (`:8081`)
- `gpt-4o`, `gpt-4o-mini` → OpenAI API
- `claude-sonnet-4-5` → mapped to `gemini-3.6-flash` (cost-free substitute)

> **Note**: For LiteLLM's ChatGPT routing to work, `OPENAI_API_KEY` must be set in your environment.

---

## MCP Tools Reference

The MCP server (`gemini_mcp_server.py`) exposes three tools:

### `ask_gemini`
| Parameter | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | *required* | Your question/message |
| `model` | `str` | `gemini-3.6-flash` | Gemini model name |
| `system_prompt` | `str \| None` | `None` | Optional system instruction |

### `ask_chatgpt`
| Parameter | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | *required* | Your question/message |
| `model` | `str` | `gpt-4o` | OpenAI model name |
| `system_prompt` | `str \| None` | `None` | Optional system instruction |

### `ask_ai`
| Parameter | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | *required* | Your question/message |
| `provider` | `str` | `gemini` | `"gemini"` or `"chatgpt"` / `"openai"` |
| `model` | `str \| None` | `None` | Model override (auto-selects if `None`) |
| `system_prompt` | `str \| None` | `None` | Optional system instruction |

---

## Available Gemini Models

These models are available through `gemini-web2api`:

| Model | Description | Output | Requires Cookie? |
|---|---|---|---|
| `gemini-3.7-flash` | Latest all-around model | ~12k chars | No |
| `gemini-3.6-flash` | All-around model | ~12k chars | No |
| `gemini-3.5-flash` | Alias for 3.6-flash | ~12k chars | No |
| `gemini-3.5-flash-thinking` | Deep thinking, longest output | ~20k chars | No |
| `gemini-3.5-flash-thinking-lite` | Adaptive thinking depth | ~15k chars | No |
| `gemini-3.1-pro` | Pro model (advanced math & code) | ~12k chars | **Yes** |
| `gemini-auto` | Auto model selection | varies | No |
| `gemini-flash-lite` | Fastest, lightweight | ~10k chars | No |

**Thinking depth**: Append `@think=N` to any model (e.g., `gemini-3.6-flash@think=0`) where 0 = deepest and 4 = shallowest.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Connection refused` on Gemini calls | Make sure `gemini-web2api` is running (`python gemini-web2api/gemini_web2api.py`) |
| `Error communicating with ChatGPT` | Set `OPENAI_API_KEY` in your environment |
| `invalid api key` from gemini-web2api | Make sure `GEMINI_API_KEY` matches a value in `gemini-web2api/config.json` → `api_keys` (default: `sk-gemini-local`) |
| Gemini returns empty/error responses | The `gemini_bl` value may be outdated — the proxy auto-updates it on startup, but try restarting gemini-web2api |
| `gemini-3.1-pro` doesn't work | Pro requires a Google cookie. Set `"cookie_file"` in `config.json` to a file containing your Gemini cookie |
| `ModuleNotFoundError: No module named 'mcp'` | Run `pip install -r requirements.txt` in your venv |
| ChatGPT 429 rate limit error | You're hitting OpenAI's rate limits. Wait and retry, or use a different model/tier |
