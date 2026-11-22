# Web API — Gemini & ChatGPT (Both FREE)

Use **Google Gemini** and **OpenAI ChatGPT** for free through local web-to-API proxies. No API keys, no billing — both proxies scrape the free web interfaces and expose them as OpenAI-compatible APIs.

| Provider | Proxy | Port | How it's free |
|---|---|---|---|
| **Gemini** | `gemini-web2api` (included) | `:8081` | Hits Gemini's public web endpoint directly — no login needed for Flash models |
| **ChatGPT** | `ChatGPT-Web2API` (you install) | `:8080` | Drives your logged-in Chrome browser via CDP — uses your free ChatGPT account |

---

## Table of Contents

- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup After Cloning](#setup-after-cloning)
  - [1. Set Up Gemini (gemini-web2api)](#1-set-up-gemini-gemini-web2api)
  - [2. Set Up ChatGPT (ChatGPT-Web2API)](#2-set-up-chatgpt-chatgpt-web2api)
  - [3. Install MCP Server Dependencies](#3-install-mcp-server-dependencies)
- [Running Everything](#running-everything)
- [Testing](#testing)
- [LiteLLM Proxy (Optional)](#litellm-proxy-optional)
- [MCP Tools Reference](#mcp-tools-reference)
- [Available Models](#available-models)
- [Configuration Reference](#configuration-reference)
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
│  gemini-web2api       │  │  ChatGPT-Web2API         │
│  localhost:8081       │  │  localhost:8080           │
│  (direct HTTP)        │  │  (Chrome browser via CDP)│
└───────────┬───────────┘  └───────────┬──────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐  ┌──────────────────────────┐
│  gemini.google.com    │  │  chatgpt.com             │
│  FREE (no login for   │  │  FREE (your browser      │
│  Flash models)        │  │  session / free account)  │
└───────────────────────┘  └──────────────────────────┘
```

**Both are free.** No API keys. No billing.

- **Gemini**: `gemini-web2api` sends requests directly to Gemini's public StreamGenerate endpoint. Flash models don't even need a login.
- **ChatGPT**: `ChatGPT-Web2API` opens a real Chrome browser, logs into your ChatGPT account once, and then proxies all API requests through the web UI. Works with free-tier ChatGPT accounts.

---

## Project Structure

```
Web_API/
├── gemini_mcp_server.py      # FastMCP server — 3 tools: ask_gemini, ask_chatgpt, ask_ai
├── main.py                   # Demo/test runner + MCP server launcher
├── requirements.txt          # Python deps (httpx, mcp)
├── pyproject.toml            # Project metadata
├── litellm-gemini.yaml       # LiteLLM config: routes both providers
├── litellm-test.yaml         # LiteLLM config: Gemini-only test
├── gemini-web2api/           # Gemini proxy (included in repo)
│   ├── gemini_web2api.py     # Standalone single-file server
│   ├── gemini_web2api/       # Modular package version
│   ├── config.json           # Gemini proxy config
│   └── requirements.txt      # Gemini proxy deps (httpx)
└── .venv/                    # Virtual environment (gitignored)
```

> `ChatGPT-Web2API` is installed separately via pip (not bundled in this repo).

---

## Prerequisites

- **Python 3.13+**
- **Google Chrome** (required for ChatGPT-Web2API — it drives Chrome via CDP)
- **A free ChatGPT account** at https://chatgpt.com (for ChatGPT access)
- **For Gemini**: Nothing! Flash models work without any account

---

## Setup After Cloning

```powershell
git clone <your-repo-url> Web_API
cd Web_API
```

### 1. Set Up Gemini (gemini-web2api)

Already included in the repo. Just install its dependency:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r gemini-web2api/requirements.txt
```

The config is at `gemini-web2api/config.json`:
```json
{
  "port": 8081,
  "host": "127.0.0.1",
  "api_keys": ["sk-gemini-local"],
  "default_model": "gemini-3.6-flash"
}
```

### 2. Set Up ChatGPT (ChatGPT-Web2API)

Install the ChatGPT proxy from GitHub:

```powershell
pip install git+https://github.com/Octo-Lex/ChatGPT-Web2API.git
```

Then create its config at `~/.chatgpt-web2api/config.json`:

```json
{
  "port": 8080,
  "host": "127.0.0.1",
  "cdp_port": 9222,
  "headless": false,
  "default_model": "auto",
  "api_keys": ["sk-chatgpt-local"]
}
```

> **First-time login**: When you run `chatgpt-web2api` for the first time, Chrome will open and navigate to chatgpt.com. Log in with your free account. After that, your session is cached at `~/.chatgpt-web2api/chrome-profile/` and you won't need to log in again.

### 3. Install MCP Server Dependencies

```powershell
pip install -r requirements.txt
```

### Quick Setup Summary (all commands)

```powershell
# From the repo root:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r gemini-web2api/requirements.txt
pip install git+https://github.com/Octo-Lex/ChatGPT-Web2API.git
```

---

## Running Everything

You need **3 terminals** (or run the proxies in the background):

### Terminal 1 — Gemini Proxy (port 8081)

```powershell
cd Web_API/gemini-web2api
python gemini_web2api.py
```

You'll see:
```
gemini-web2api v1.1.0
  Listening: http://0.0.0.0:8081
  Base URL:  http://localhost:8081/v1
  Models:    gemini-3.7-flash, gemini-3.6-flash, ...
```

### Terminal 2 — ChatGPT Proxy (port 8080)

```powershell
chatgpt-web2api
```

Chrome will open. If it's your first time, log into ChatGPT. Then you'll see:
```
ChatGPT-Web2API running on http://127.0.0.1:8080
```

### Terminal 3 — MCP Server

```powershell
cd Web_API
.\.venv\Scripts\Activate.ps1
python gemini_mcp_server.py
```

Or run the demo to test everything:
```powershell
python main.py
```

---

## Testing

### Quick Demo (tests both providers)

```powershell
# Make sure both proxies are running first!
python main.py
```

Expected output:
```
=== Web API Demo: Gemini & ChatGPT (Both FREE) ===

[1] Testing Gemini (via gemini-web2api on :8081)...
Gemini: I am Gemini, a large language model created by Google.

[2] Testing ChatGPT (via chatgpt-web2api on :8080)...
ChatGPT: I'm ChatGPT, made by OpenAI.

[3] Testing ask_ai (unified tool)...
ask_ai(gemini): I am Gemini...
```

### Test Gemini with curl

```powershell
# PowerShell
curl.exe --% http://127.0.0.1:8081/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-gemini-local" -d "{\"model\":\"gemini-3.6-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}"
```

### Test ChatGPT with curl

```powershell
# PowerShell
curl.exe --% http://127.0.0.1:8080/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer sk-chatgpt-local" -d "{\"model\":\"auto\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}"
```

### Test with Python (OpenAI SDK)

```python
from openai import OpenAI

# Gemini (FREE via local proxy)
gemini = OpenAI(base_url="http://localhost:8081/v1", api_key="sk-gemini-local")
print(gemini.chat.completions.create(
    model="gemini-3.6-flash",
    messages=[{"role": "user", "content": "What model are you?"}]
).choices[0].message.content)

# ChatGPT (FREE via local proxy)
chatgpt = OpenAI(base_url="http://localhost:8080/v1", api_key="sk-chatgpt-local")
print(chatgpt.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "What model are you?"}]
).choices[0].message.content)
```

---

## LiteLLM Proxy (Optional)

Route all models through a **single endpoint** on port 4000:

```powershell
pip install litellm[proxy]
litellm --config litellm-gemini.yaml --port 4000
```

This gives you `http://localhost:4000` routing:
- `gemini-3.6-flash` → gemini-web2api (`:8081`) — FREE
- `gpt-4o`, `gpt-4o-mini`, `chatgpt-auto` → chatgpt-web2api (`:8080`) — FREE
- `claude-sonnet-4-5` → mapped to gemini-3.6-flash — FREE

---

## MCP Tools Reference

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
| `model` | `str` | `auto` | ChatGPT model name |
| `system_prompt` | `str \| None` | `None` | Optional system instruction |

### `ask_ai`
| Parameter | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | *required* | Your question/message |
| `provider` | `str` | `gemini` | `"gemini"` or `"chatgpt"` |
| `model` | `str \| None` | `None` | Auto-selects if `None` |
| `system_prompt` | `str \| None` | `None` | Optional system instruction |

---

## Available Models

### Gemini (via gemini-web2api — FREE, no login)

| Model | Description | Output | Login needed? |
|---|---|---|---|
| `gemini-3.7-flash` | Latest all-around | ~12k chars | No |
| `gemini-3.6-flash` | All-around | ~12k chars | No |
| `gemini-3.5-flash-thinking` | Deep thinking, longest output | ~20k chars | No |
| `gemini-3.5-flash-thinking-lite` | Adaptive thinking | ~15k chars | No |
| `gemini-3.1-pro` | Advanced (math & code) | ~12k chars | Yes (cookie) |
| `gemini-auto` | Auto model selection | varies | No |
| `gemini-flash-lite` | Fastest, lightweight | ~10k chars | No |

### ChatGPT (via ChatGPT-Web2API — FREE, your account)

| Model | Description |
|---|---|
| `auto` | Let ChatGPT pick the best model (recommended) |
| `gpt-4o` | GPT-4o |
| `gpt-4o-mini` | GPT-4o Mini (lighter) |
| Other models | Whatever your ChatGPT account has access to |

> The available ChatGPT models depend on your account tier (free, Plus, Pro). The `auto` model works for everyone.

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_BASE_URL` | `http://127.0.0.1:8081/v1` | Gemini proxy URL |
| `GEMINI_API_KEY` | `sk-gemini-local` | Must match gemini-web2api's `config.json` → `api_keys` |
| `CHATGPT_BASE_URL` | `http://127.0.0.1:8080/v1` | ChatGPT proxy URL |
| `CHATGPT_API_KEY` | `sk-chatgpt-local` | Must match chatgpt-web2api's `config.json` → `api_keys` |

### gemini-web2api config (`gemini-web2api/config.json`)

| Field | Default | Description |
|---|---|---|
| `port` | `8081` | Listening port |
| `api_keys` | `["sk-gemini-local"]` | API keys for auth (empty = no auth) |
| `cookie_file` | `null` | Google cookie file (only needed for Pro model) |
| `proxy` | `null` | HTTP proxy if needed |
| `temporary_chats` | `false` | Don't save chats to Gemini history |

### ChatGPT-Web2API config (`~/.chatgpt-web2api/config.json`)

| Field | Default | Description |
|---|---|---|
| `port` | `8080` | Listening port |
| `api_keys` | `["sk-chatgpt-local"]` | API keys for auth |
| `headless` | `false` | Run Chrome without GUI (not recommended — may trigger bot detection) |
| `cdp_port` | `9222` | Chrome DevTools Protocol port |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `Connection refused` on `:8081` | Start gemini-web2api: `cd gemini-web2api && python gemini_web2api.py` |
| `Connection refused` on `:8080` | Start chatgpt-web2api: `chatgpt-web2api` |
| ChatGPT proxy says "not logged in" | Chrome should auto-open chatgpt.com — log in with your free account |
| ChatGPT session expired | Delete `~/.chatgpt-web2api/chrome-profile/` and log in again, or restart `chatgpt-web2api` |
| `invalid api key` from Gemini proxy | Your `GEMINI_API_KEY` doesn't match `config.json` → `api_keys` (default: `sk-gemini-local`) |
| `invalid api key` from ChatGPT proxy | Your `CHATGPT_API_KEY` doesn't match the chatgpt-web2api config (default: `sk-chatgpt-local`) |
| Gemini returns empty responses | Restart gemini-web2api (the `gemini_bl` value may be stale — it auto-updates on start) |
| `gemini-3.1-pro` not working | Pro requires a Google cookie. Set `"cookie_file"` in `gemini-web2api/config.json` |
| `ModuleNotFoundError: mcp` | Run `pip install -r requirements.txt` |
| `chatgpt-web2api` command not found | Run `pip install git+https://github.com/Octo-Lex/ChatGPT-Web2API.git` |
| Chrome doesn't open | Make sure Google Chrome is installed and accessible in your PATH |
