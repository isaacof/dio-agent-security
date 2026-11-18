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

LOGIN_PAGE = """<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Lab - Login (corrigido)</title></head>
<body style="font-family:system-ui;max-width:32rem;margin:4rem auto">
  <h1>Laboratorio de login - versao corrigida</h1>
  <form method="post" action="/login">
    <p><label>Usuario<br><input name="username" autocomplete="off"></label></p>
    <p><label>Senha<br><input name="password" type="password"></label></p>
    <p><button type="submit">Entrar</button></p>
  </form>
  {mensagem}
</body>
</html>
"""


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
        return conn.execute(
            "SELECT id, username, role FROM users "
            "WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
    finally:
        conn.close()


def page(message: str = "") -> bytes:
    return LOGIN_PAGE.format(mensagem=message).encode("utf-8")


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
        self._send(HTTPStatus.OK, page())

    def do_POST(self) -> None:  # noqa: N802 - assinatura da stdlib
        if self.path != "/login":
            self._send(HTTPStatus.NOT_FOUND, b"<h1>404</h1>")
            return
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]

        row = authenticate(username, password)
        if row is None:
            body = page('<p style="color:#b00020">Credenciais invalidas.</p>')
            self._send(HTTPStatus.UNAUTHORIZED, body)
            return

        body = page(
            f"<p>Bem-vindo, <strong>{html.escape(row['username'])}</strong> "
            f"(papel: {html.escape(row['role'])}).</p>"
        )
        self._send(HTTPStatus.OK, body)

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
