import asyncio
import sys
from gemini_mcp_server import ask_gemini, ask_chatgpt, ask_ai, mcp


async def demo():
    prompt = "Hello! Reply with one short sentence stating your model name."

    print("==================================================")
    print("      Testing Web API (Gemini & ChatGPT - FREE)   ")
    print("==================================================\n")

    print("[1] Testing Gemini (via gemini_web2api.py on :8081)...")
    gemini_res = await ask_gemini(prompt)
    print(f"Gemini: {gemini_res}\n")

    print("[2] Testing ChatGPT (FREE via chatgpt_web2api / built-in engine)...")
    chatgpt_res = await ask_chatgpt(prompt)
    print(f"ChatGPT: {chatgpt_res}\n")

    print("[3] Testing ask_ai unified tool...")
    ai_gemini = await ask_ai(prompt, provider="gemini")
    print(f"ask_ai(gemini):  {ai_gemini[:80]}...")
    ai_chatgpt = await ask_ai(prompt, provider="chatgpt")
    print(f"ask_ai(chatgpt): {ai_chatgpt[:80]}...")
    print("\nAll tests completed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Starting FastMCP Server...")
        mcp.run()
    else:
        asyncio.run(demo())
