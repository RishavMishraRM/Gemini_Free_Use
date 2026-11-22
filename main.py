import asyncio
import os
import sys
from gemini_mcp_server import ask_gemini, ask_chatgpt, ask_ai, mcp


async def run_demo():
    print("=== Web API Demo: Gemini & ChatGPT (Both FREE) ===")

    prompt = "Hello! Please reply in one short sentence stating your model name."

    print("\n[1] Testing Gemini (via gemini-web2api on :8081)...")
    gemini_resp = await ask_gemini(prompt)
    print(f"Gemini: {gemini_resp}")

    print("\n[2] Testing ChatGPT (via chatgpt-web2api on :8080)...")
    chatgpt_resp = await ask_chatgpt(prompt)
    print(f"ChatGPT: {chatgpt_resp}")

    print("\n[3] Testing ask_ai (unified tool)...")
    unified_resp = await ask_ai(prompt, provider="gemini")
    print(f"ask_ai(gemini): {unified_resp}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Starting FastMCP Server...")
        mcp.run()
    else:
        print("Running demo (use 'python main.py server' to start the MCP server):")
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()
