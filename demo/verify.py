#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py - Prova, por HTTP, que a versao vulneravel aceita o bypass e que a
versao corrigida recusa o mesmo payload.

Roda as duas aplicacoes em portas efemeras, na propria maquina, com um banco
temporario. Nada sai de 127.0.0.1.

Uso:
    python verify.py
"""

from __future__ import annotations

import http.client
import os
import re
import sys
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlencode

BASE_DIR = Path(__file__).resolve().parent

# titulo, usuario, senha, esperado em app.py, esperado em app_fixed.py
CASES = [
    ("credencial valida", "admin", "admin123", 200, 200),
    ("senha errada", "admin", "senha-errada", 401, 401),
    ("bypass OR 1=1", "' OR '1'='1' --", "x", 200, 401),
    ("comentario apos usuario", "admin'--", "x", 200, 401),
    ("bypass no campo senha", "admin", "' OR '1'='1' --", 200, 401),
]


def start(module) -> tuple[object, int]:
    server = module.make_server(0, "127.0.0.1")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def attempt(port: int, username: str, password: str) -> tuple[int, str]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    body = urlencode({"username": username, "password": password})
    conn.request(
        "POST",
        "/login",
        body=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response = conn.getresponse()
    text = response.read().decode("utf-8", "replace")
    conn.close()
    return response.status, text


def efeito(text: str) -> str:
    """Resume o que a pagina respondeu, para o relatorio."""
    match = re.search(r"Bem-vindo.*?</p>", text, re.S)
    if match:
        limpo = re.sub(r"<[^>]+>", "", match.group(0))
        return re.sub(r"\s+", " ", limpo).strip()[:60]
    return "Credenciais invalidas" if "invalidas" in text else "sem mensagem"


def corpo_confere(status: int, text: str) -> bool:
    """Confere tambem o corpo: status 200 so vale se a pagina autenticou."""
    if status == 200:
        return "Bem-vindo" in text
    return "Credenciais invalidas" in text


def run() -> int:
    with tempfile.TemporaryDirectory(prefix="lab-sqli-") as tmp:
        # LAB_DB precisa ser definido antes do import: os dois modulos leem o
        # caminho do banco no nivel do modulo, nao dentro das funcoes.
        os.environ["LAB_DB"] = str(Path(tmp) / "lab.db")
        sys.path.insert(0, str(BASE_DIR))
        import app as vuln  # noqa: PLC0415
        import app_fixed as fixed  # noqa: PLC0415

        server_v, port_v = start(vuln)
        server_f, port_f = start(fixed)
        try:
            print("=" * 78)
            print("  SQL Injection no login - verificacao automatizada")
            print("  alvo: 127.0.0.1 (laboratorio local)")
            print("=" * 78)

            failures = 0
            for titulo, user, pwd, esperado_vuln, esperado_fixed in CASES:
                print(f"\n[{titulo}]")
                print(f"  payload: usuario={user!r} senha={pwd!r}")

                status_v, texto_v = attempt(port_v, user, pwd)
                status_f, texto_f = attempt(port_f, user, pwd)

                ok_v = status_v == esperado_vuln and corpo_confere(status_v, texto_v)
                ok_f = status_f == esperado_fixed and corpo_confere(
                    status_f, texto_f
                )
                failures += int(not ok_v) + int(not ok_f)

                print(
                    f"  app.py        -> HTTP {status_v} | {efeito(texto_v)} "
                    f"| esperado {esperado_vuln} {'OK' if ok_v else 'FALHOU'}"
                )
                print(
                    f"  app_fixed.py  -> HTTP {status_f} | {efeito(texto_f)} "
                    f"| esperado {esperado_fixed} {'OK' if ok_f else 'FALHOU'}"
                )
        finally:
            server_v.shutdown()
            server_v.server_close()
            server_f.shutdown()
            server_f.server_close()

    print("\n" + "=" * 78)
    if failures:
        print(f"  RESULTADO: {failures} verificacao(oes) falharam")
        print("=" * 78)
        return 1

    print(f"  RESULTADO: comportamento esperado nos {len(CASES)} casos")
    print("  app.py aceita o bypass; app_fixed.py recusa o mesmo payload.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
