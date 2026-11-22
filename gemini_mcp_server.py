import asyncio
import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Gemini & ChatGPT API")

# ── Gemini (gemini_web2api.py on :8081 — FREE) ──────────────────────────────
GEMINI_URL = os.getenv("GEMINI_BASE_URL", "http://127.0.0.1:8081/v1")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "sk-gemini-local")

# ── ChatGPT (chatgpt_web2api.py on :8080 or direct — FREE) ──────────────────
CHATGPT_URL = os.getenv("CHATGPT_BASE_URL", "http://127.0.0.1:8080/v1")
CHATGPT_KEY = os.getenv("CHATGPT_API_KEY", "sk-chatgpt-local")


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _chat(base_url: str, api_key: str, model: str,
                prompt: str, system_prompt: str | None) -> str:
    """Send chat request to any OpenAI-compatible API endpoint."""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json={"model": model, "messages": messages, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _chatgpt_direct(prompt: str, model: str, system_prompt: str | None) -> str:
    """Fallback direct query for ChatGPT using built-in g4f."""
    from g4f.client import Client
    client = Client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    m = model if model not in ("auto", "default", "") else "gpt-4o-mini"
    res = client.chat.completions.create(model=m, messages=messages)
    return res.choices[0].message.content or ""


# ── MCP Tools ────────────────────────────────────────────────────────────────

@mcp.tool()
async def ask_gemini(
    prompt: str,
    model: str = "gemini-3.6-flash",
    system_prompt: str | None = None,
) -> str:
    """Ask Google Gemini (FREE via local gemini_web2api.py proxy on port 8081).

    Args:
        prompt: User question or message.
        model: 'gemini-3.6-flash', 'gemini-3.5-flash-thinking', 'gemini-3.1-pro', 'gemini-auto'
        system_prompt: Optional instructions for the model.
    """
    try:
        return await _chat(GEMINI_URL, GEMINI_KEY, model, prompt, system_prompt)
    except Exception as e:
        return f"Gemini error: {e}"


@mcp.tool()
async def ask_chatgpt(
    prompt: str,
    model: str = "gpt-4o-mini",
    system_prompt: str | None = None,
) -> str:
    """Ask OpenAI ChatGPT (FREE — via local chatgpt_web2api.py or direct built-in engine).

    Args:
        prompt: User question or message.
        model: 'gpt-4o-mini', 'gpt-4o', 'auto'
        system_prompt: Optional instructions for the model.
    """
    # 1. Try local HTTP proxy (port 8080)
    try:
        return await _chat(CHATGPT_URL, CHATGPT_KEY, model, prompt, system_prompt)
    except Exception:
        pass

    # 2. Seamless fallback: built-in direct provider
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _chatgpt_direct, prompt, model, system_prompt)
    except Exception as e:
        return f"ChatGPT error: {e}"


@mcp.tool()
async def ask_ai(
    prompt: str,
    provider: str = "gemini",
    model: str | None = None,
    system_prompt: str | None = None,
) -> str:
    """Query either Gemini or ChatGPT. Both are completely FREE.

    Args:
        prompt: User question or message.
        provider: 'gemini' or 'chatgpt' (default: 'gemini').
        model: Specific model or leave None for default.
        system_prompt: Optional instructions.
    """
    if provider.lower() in ("chatgpt", "openai"):
        return await ask_chatgpt(prompt, model=model or "gpt-4o-mini", system_prompt=system_prompt)
    return await ask_gemini(prompt, model=model or "gemini-3.6-flash", system_prompt=system_prompt)


if __name__ == "__main__":
    mcp.run()
