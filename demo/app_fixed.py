#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app_fixed.py - A mesma aplicacao, com consulta parametrizada.

Diferenca em relacao a app.py: o SQL e fixo e os valores entram como
parametros. O driver do banco trata cada valor como dado, nunca como
comando, entao aspas e comentarios digitados no formulario nao mudam a
estrutura da consulta.

Uso:
    python app_fixed.py            # sobe em http://127.0.0.1:8000
    python app_fixed.py --port 8081
"""

from __future__ import annotations

import argparse
import html
import os
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("LAB_DB", BASE_DIR / "lab.db"))

SEED = [
    ("admin", "admin123", "admin"),
    ("alice", "alice123", "user"),
    ("bob", "bob123", "user"),
]

STYLE = """
:root{--bg:#f1f5f9;--card:#fff;--ink:#0f172a;--muted:#64748b;--line:#e2e8f0}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);
color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:32px}
.card{width:100%;max-width:660px;background:var(--card);border:1px solid var(--line);
border-radius:16px;padding:32px;box-shadow:0 24px 48px -28px rgba(15,23,42,.4)}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px}
h1{font-size:23px;margin:0}
.sub{margin:4px 0 24px;color:var(--muted);font-size:13px}
.badge{font-size:11px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
padding:6px 11px;border-radius:999px;white-space:nowrap}
.danger{background:#fee2e2;color:#991b1b}
.safe{background:#dcfce7;color:#166534}
label{display:block;font-size:13px;font-weight:600;color:#334155;margin-bottom:6px}
input{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;font:inherit}
input:focus{outline:2px solid #93c5fd;border-color:#60a5fa}
button{margin-top:16px;padding:10px 20px;border:0;border-radius:8px;background:#0f172a;
color:#fff;font:inherit;font-weight:600;cursor:pointer}
button:hover{background:#1e293b}
.field{margin-bottom:14px}
.result{margin-top:24px;padding:13px 16px;border-radius:10px;font-size:14px}
.ok{background:#f0fdf4;border:1px solid #bbf7d0;color:#166534}
.deny{background:#fef2f2;border:1px solid #fecaca;color:#991b1b}
.code{margin-top:18px}
.code h2{font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);
margin:0 0 6px;font-weight:700}
pre{margin:0;background:#0f172a;color:#e2e8f0;padding:14px 16px;border-radius:10px;
overflow-x:auto;font:13px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace;
white-space:pre-wrap;word-break:break-word}
.mark{color:#86efac;font-weight:700}
footer{margin-top:22px;font-size:12px;color:var(--muted)}
"""

FORM = """
  <form method="post" action="/login">
    <div class="field"><label for="u">Usuario</label>
      <input id="u" name="username" autocomplete="off" autofocus></div>
    <div class="field"><label for="p">Senha</label>
      <input id="p" name="password" type="password"></div>
    <button type="submit">Entrar</button>
  </form>
"""

QUERY = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = connect()
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)"
        )
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", SEED
            )
    conn.close()


def authenticate(username: str, password: str) -> sqlite3.Row | None:
    """Autentica com consulta parametrizada: o valor nunca vira comando."""
    conn = connect()
    try:
        return conn.execute(QUERY, (username, password)).fetchone()
    finally:
        conn.close()


def render(result_html: str = "", code_html: str = "") -> bytes:
    return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab SQL Injection - corrigida</title><style>{STYLE}</style></head>
<body><main class="card">
  <div class="top"><h1>Laboratorio de login</h1>
    <span class="badge safe">corrigida</span></div>
  <p class="sub">DIO Agent &middot; laboratorio de SQL Injection &middot; dado ficticio</p>
  {FORM}
  {result_html}
  {code_html}
  <footer>127.0.0.1 &middot; app_fixed.py &middot; consulta parametrizada</footer>
</main></body></html>""".encode("utf-8")


def code_block(username: str, password: str) -> str:
    params = html.escape(f"({username!r}, {password!r})")
    return (
        '<div class="code"><h2>Consulta executada</h2>'
        f"<pre>{html.escape(QUERY)}</pre></div>"
        '<div class="code"><h2>Parametros enviados ao driver</h2>'
        f'<pre><span class="mark">{params}</span></pre></div>'
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "LabLoginFixed/1.0"

    def _send(self, status: HTTPStatus, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - assinatura da stdlib
        if self.path not in ("/", "/login"):
            self._send(HTTPStatus.NOT_FOUND, b"<h1>404</h1>")
            return
        self._send(HTTPStatus.OK, render())

    def do_POST(self) -> None:  # noqa: N802 - assinatura da stdlib
        if self.path != "/login":
            self._send(HTTPStatus.NOT_FOUND, b"<h1>404</h1>")
            return
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]

        row = authenticate(username, password)
        block = code_block(username, password)
        if row is None:
            result = '<div class="result deny">Credenciais invalidas.</div>'
            self._send(HTTPStatus.UNAUTHORIZED, render(result, block))
            return

        result = (
            '<div class="result ok">Bem-vindo, '
            f"<strong>{html.escape(row['username'])}</strong> "
            f"(papel: {html.escape(row['role'])}).</div>"
        )
        self._send(HTTPStatus.OK, render(result, block))

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[app_fixed] {self.address_string()} {fmt % args}", flush=True)


def make_server(port: int = 8000, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    init_db()
    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Login de laboratorio (corrigido).")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = make_server(args.port, args.host)
    print(f"[app_fixed] http://{args.host}:{args.port}  (Ctrl+C para parar)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
