import asyncio
import os
import sys
from gemini_mcp_server import ask_gemini, ask_chatgpt, ask_ai, mcp


async def run_demo():
    print("=== Web API Demo: Gemini & ChatGPT ===")
    
    prompt = "Hello! Please reply in one short sentence stating your model name."
    
    print("\n[1] Testing Gemini (via Web2API)...")
    gemini_resp = await ask_gemini(prompt)
    print(f"Gemini: {gemini_resp}")
    
    print("\n[2] Testing ChatGPT...")
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("CHATGPT_API_KEY"):
        print("Note: OPENAI_API_KEY or CHATGPT_API_KEY is not set. Set it to query ChatGPT.")
    chatgpt_resp = await ask_chatgpt(prompt)
    print(f"ChatGPT: {chatgpt_resp}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Starting FastMCP Server...")
        mcp.run()
    else:
        print("Running demo check (use 'python main.py server' to start the MCP server directly):")
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()
