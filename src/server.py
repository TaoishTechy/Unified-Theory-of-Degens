#!/usr/bin/env python3
"""
server.py
=========

Builds index.html, then serves the project directory.

Run:
    python3 src/server.py

Open:
    http://localhost:8000/index.html
"""

from __future__ import annotations

import http.server
import os
import socketserver
from pathlib import Path

from atlas import build_atlas


ROOT = Path(__file__).resolve().parent.parent
PORT = 8000


def run_server(port: int = PORT):
    os.chdir(ROOT)

    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"[INFO] Serving directory: {ROOT}")
        print(f"[INFO] Open: http://localhost:{port}/index.html")
        httpd.serve_forever()


if __name__ == "__main__":
    build_atlas()
    run_server()
