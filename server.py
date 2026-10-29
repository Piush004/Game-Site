#!/usr/bin/env python3
"""Serve the site and save quiz answers into Documents/Dineth-Answers."""

import json
import socket
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANSWERS = Path.home() / "Documents" / "Dineth-Answers"
PORT = 8765

QUESTIONS = [
    ("like", "Do you like your girlfriend?"),
    ("mean", "Is your girlfriend mean?"),
    ("support", "Does your girlfriend support you?"),
    ("pretty", "Is your girlfriend pretty?"),
    ("forever", "Is your girlfriend your forever partner?"),
    ("love", "Do you love your girlfriend?"),
    ("message", "Do you want to receive the message from your girlfriend?"),
]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/save-answers":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Expected JSON")
            return

        ANSWERS.mkdir(parents=True, exist_ok=True)
        moment = datetime.now()
        path = ANSWERS / f"{moment.strftime('%Y-%m-%d-%H-%M-%S')}.txt"
        lines = [
            f"Saved {moment.strftime('%A, %B %-d, %Y at %-I:%M %p')}",
            f"Name: {str(data.get('name', '')).strip() or 'Dineth'}",
            "",
        ]
        for key, label in QUESTIONS:
            value = str(data.get(key, "")).strip().lower()
            answer = {"yes": "Yes", "no": "No"}.get(value, value or "Not answered")
            lines.append(f"{label} {answer}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        body = json.dumps({"ok": True, "file": str(path)}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def phone_address():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


if __name__ == "__main__":
    ANSWERS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"On this Mac: http://127.0.0.1:{PORT}", flush=True)
    lan = phone_address()
    if lan and not lan.startswith("127."):
        print(f"On another phone (same Wi-Fi): http://{lan}:{PORT}", flush=True)
    print(f"Answers: {ANSWERS}", flush=True)
    server.serve_forever()
