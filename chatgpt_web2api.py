#!/usr/bin/env python3
"""
chatgpt_web2api.py - Free ChatGPT to OpenAI API Proxy.

Converts free ChatGPT access into an OpenAI-compatible API server.
Zero API key required. Works locally on http://127.0.0.1:8080/v1.

Usage:
    python chatgpt_web2api.py [--port 8080]
"""

import json
import os
import sys
import time
import uuid
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

try:
    import g4f
    from g4f.client import Client as G4FClient
    HAS_G4F = True
except ImportError:
    HAS_G4F = False

PORT = int(os.getenv("CHATGPT_PORT", "8080"))
HOST = os.getenv("CHATGPT_HOST", "127.0.0.1")
API_KEYS = [os.getenv("CHATGPT_API_KEY", "sk-chatgpt-local")]

MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "auto",
    "chatgpt-4o-latest",
]


class ChatGPTHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        client_ip = self.client_address[0] if self.client_address else "-"
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {client_ip} {fmt % args}\n")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        if not API_KEYS or API_KEYS == [""]:
            return True
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            if token in API_KEYS:
                return True
        api_key = self.headers.get("x-api-key")
        if api_key and api_key in API_KEYS:
            return True
        return False

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_json({
                "status": "ok",
                "service": "chatgpt-web2api",
                "models": MODELS
            })
            return

        if not self._authorized():
            self.send_json({"error": {"message": "Invalid API key"}}, 401)
            return

        if self.path in ("/v1/models", "/models"):
            data = [
                {
                    "id": m,
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "openai"
                }
                for m in MODELS
            ]
            self.send_json({"object": "list", "data": data})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if not self._authorized():
            self.send_json({"error": {"message": "Invalid API key"}}, 401)
            return

        if self.path in ("/v1/chat/completions", "/chat/completions"):
            self.handle_chat_completions()
        else:
            self.send_json({"error": "Not found"}, 404)

    def handle_chat_completions(self):
        if not HAS_G4F:
            self.send_json({"error": {"message": "g4f library not installed. Run: pip install g4f"}}, 500)
            return

        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            self.send_json({"error": {"message": "Empty request body"}}, 400)
            return

        body = self.rfile.read(length)
        try:
            req = json.loads(body)
        except Exception:
            self.send_json({"error": {"message": "Invalid JSON"}}, 400)
            return

        model = req.get("model", "gpt-4o-mini")
        messages = req.get("messages", [])
        if not messages:
            self.send_json({"error": {"message": "Messages list cannot be empty"}}, 400)
            return

        # Normalize model
        if model in ("auto", "default", ""):
            model = "gpt-4o-mini"

        try:
            client = G4FClient()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            content = response.choices[0].message.content or ""
            cid = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            res_payload = {
                "id": cid,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(str(messages)) // 4,
                    "completion_tokens": len(content) // 4,
                    "total_tokens": (len(str(messages)) + len(content)) // 4
                }
            }
            self.send_json(res_payload)
        except Exception as e:
            self.send_json({"error": {"message": f"ChatGPT generation error: {str(e)}"}}, 500)


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(description="Free ChatGPT Web2API Proxy")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to listen on (default: {PORT})")
    parser.add_argument("--host", type=str, default=HOST, help=f"Host interface (default: {HOST})")
    args = parser.parse_args()

    server = ThreadedServer((args.host, args.port), ChatGPTHandler)
    print("=" * 50)
    print("  ChatGPT Web2API (FREE)")
    print(f"  Listening: http://{args.host}:{args.port}")
    print(f"  Base URL:  http://127.0.0.1:{args.port}/v1")
    print(f"  API Key:   {API_KEYS[0] if API_KEYS else 'none'}")
    print(f"  Models:    {', '.join(MODELS)}")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ChatGPT Web2API server...")
        server.shutdown()


if __name__ == "__main__":
    main()
