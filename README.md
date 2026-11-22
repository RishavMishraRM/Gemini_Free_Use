# Web API (Gemini & ChatGPT)

Unified FastMCP server and proxy configuration for **Google Gemini** (via local `gemini-web2api`) and **ChatGPT** (via OpenAI API or compatible Web2API).

## Features

- **Gemini Tool (`ask_gemini`)**: Connects to the local `gemini-web2api` service (default: `http://127.0.0.1:8081/v1`).
- **ChatGPT Tool (`ask_chatgpt`)**: Connects to OpenAI API or custom ChatGPT proxy (`OPENAI_BASE_URL` / `CHATGPT_BASE_URL`).
- **Unified Tool (`ask_ai`)**: Allows querying either provider (`provider="gemini"` or `provider="chatgpt"`).
- **LiteLLM Configuration**: Includes configs for both Gemini and ChatGPT models in `litellm-gemini.yaml`.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_BASE_URL` | `http://127.0.0.1:8081/v1` | URL for the gemini-web2api server |
| `GEMINI_API_KEY` | `sk-gemini-local` | API key configured in gemini-web2api |
| `CHATGPT_BASE_URL` or `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Base URL for ChatGPT / OpenAI |
| `CHATGPT_API_KEY` or `OPENAI_API_KEY` | *(empty)* | OpenAI API key |

## Running the Server

### 1. Start Gemini Web2API (if using Gemini)
```powershell
cd gemini-web2api
python gemini_web2api.py
```

### 2. Run the MCP Server
```powershell
python gemini_mcp_server.py
```
or:
```powershell
python main.py server
```

### 3. Run Demo / Test Script
```powershell
python main.py
```
