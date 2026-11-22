import os
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Gemini & ChatGPT API Server")

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

# Gemini Settings (defaulting to local gemini-web2api)
GEMINI_URL = os.getenv(
    "GEMINI_BASE_URL",
    "http://127.0.0.1:8081/v1"
)

GEMINI_KEY = os.getenv(
    "GEMINI_API_KEY",
    "sk-gemini-local"
)

# ChatGPT / OpenAI Settings (defaults to OpenAI API or custom proxy/web2api)
CHATGPT_URL = os.getenv(
    "CHATGPT_BASE_URL",
    os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

CHATGPT_KEY = os.getenv(
    "CHATGPT_API_KEY",
    os.getenv("OPENAI_API_KEY", "")
)


# ----------------------------------------------------
# MCP Tools
# ----------------------------------------------------

@mcp.tool()
async def ask_gemini(
    prompt: str,
    model: str = "gemini-3.6-flash",
    system_prompt: str | None = None
) -> str:
    """Ask a Gemini model through the local gemini-web2api server.

    Args:
        prompt: The question or message for Gemini.
        model: Model to use (e.g., 'gemini-3.6-flash', 'gemini-3.5-flash-thinking', 'gemini-3.1-pro', 'gemini-auto').
        system_prompt: Optional system prompt to instruct the model.
    """
    headers = {
        "Authorization": f"Bearer {GEMINI_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{GEMINI_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"Gemini API Error ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error communicating with Gemini: {str(e)}"


@mcp.tool()
async def ask_chatgpt(
    prompt: str,
    model: str = "gpt-4o",
    system_prompt: str | None = None
) -> str:
    """Ask a ChatGPT / OpenAI model through OpenAI API or compatible proxy/Web2API.

    Args:
        prompt: The question or message for ChatGPT.
        model: Model to use (e.g., 'gpt-4o', 'gpt-4o-mini', 'o1', 'o3-mini', 'gpt-4-turbo').
        system_prompt: Optional system prompt to instruct the model.
    """
    headers = {
        "Content-Type": "application/json"
    }
    if CHATGPT_KEY:
        headers["Authorization"] = f"Bearer {CHATGPT_KEY}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{CHATGPT_URL.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"ChatGPT API Error ({e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error communicating with ChatGPT: {str(e)}"


@mcp.tool()
async def ask_ai(
    prompt: str,
    provider: str = "gemini",
    model: str | None = None,
    system_prompt: str | None = None
) -> str:
    """Query either Gemini or ChatGPT based on provider selection.

    Args:
        prompt: The question or message.
        provider: 'gemini' or 'chatgpt' / 'openai' (default is 'gemini').
        model: Optional model override. Defaults to 'gemini-3.6-flash' or 'gpt-4o'.
        system_prompt: Optional system prompt.
    """
    if provider.lower() in ("chatgpt", "openai"):
        selected_model = model or "gpt-4o"
        return await ask_chatgpt(prompt, model=selected_model, system_prompt=system_prompt)
    else:
        selected_model = model or "gemini-3.6-flash"
        return await ask_gemini(prompt, model=selected_model, system_prompt=system_prompt)


if __name__ == "__main__":
    mcp.run()
