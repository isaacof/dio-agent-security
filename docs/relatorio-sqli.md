# Relatório de análise — SQL Injection no login

Relatório no formato que a skill `vulnerability-analysis` produz, aplicado ao
laboratório [`demo/`](../demo/). Foi gerado a partir da conversa registrada em
[`demo/evidence/agent_session.md`](../demo/evidence/agent_session.md) e da
verificação em [`demo/evidence/verify_output.txt`](../demo/evidence/verify_output.txt).

## Resumo

| Campo | Valor |
|---|---|
| Falha | SQL Injection na autenticação, por concatenação de string |
| Local | `demo/app.py`, `authenticate()` (linhas 73–76) |
| CWE | CWE-89 — Improper Neutralization of Special Elements used in an SQL Command |
| OWASP Top 10 | A03:2021 Injection |
| MITRE ATT&CK | T1190 só se a aplicação estiver exposta à internet; no laboratório local, não se aplica |
| Impacto | **Alto** em potencial: bypass de login e leitura da tabela `users`. No material atual, **baixo**, porque o dado é fictício e descartável |
| Probabilidade | **Baixa**: bind em `127.0.0.1`, sem exposição, exige acesso à máquina |
| Severidade | **Média** (Alto × Baixa) no laboratório; **Crítica** se o padrão for reutilizado em serviço exposto |
| Prazo sugerido | Antes de reutilizar o padrão em qualquer outro projeto |

## Evidência

Trecho verificado no arquivo:

```python
query = (
    "SELECT id, username, role FROM users "
    f"WHERE username = '{username}' AND password = '{password}'"
)
```

Os valores vêm de `parse_qs` no `do_POST` e chegam sem tratamento. O mesmo
arquivo já usa `?` corretamente no `INSERT` do `init_db()`, ou seja, a forma
segura já estava ali a três funções de distância.

**Verificado:** leitura do código, execução local e resultado do `verify.py`.
**Não verificado:** comportamento atrás de proxy, WAF ou qualquer camada que
não existe no laboratório.

## Como a falha funciona

Fluxo: `username` do POST → concatenação → `conn.execute(query)`.

```text
' OR '1'='1' --
```

- `'` fecha a string do campo `username`;
- `OR '1'='1'` torna a condição sempre verdadeira;
- `--` comenta o resto da consulta, anulando a checagem de senha.

Consulta resultante, exibida na própria página:

```sql
SELECT id, username, role FROM users WHERE username = '' OR '1'='1' --' AND password = 'x'
```

Efeito observado: autenticação como `admin`, sem conhecer a senha.

O que a falha **não** permite neste código: empilhar comandos (o driver executa
um statement por chamada), obter shell ou derrubar o serviço. `fetchone()`
limita o retorno a uma linha.

## Correção

**Causa raiz:** a consulta é montada com o valor, então a entrada muda a
estrutura do comando.

Correção aplicada em [`demo/app_fixed.py`](../demo/app_fixed.py):

```python
QUERY = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
conn.execute(QUERY, (username, password))
```

O driver trata cada valor como dado. A consulta exibida na página continua
idêntica, independentemente do que for digitado; os parâmetros aparecem
separados.

**Defesa em profundidade recomendada:**

- bind explícito em `127.0.0.1` ou remoção da opção `--host`;
- limite de tentativas por IP e por usuário;
- log de falha de autenticação sem registrar a senha;
- mensagem de erro genérica — já presente;
- teste automatizado cobrindo o payload.

**Efeito colateral:** nenhum para a consulta parametrizada. A migração para
hash de senha exige mudar o schema e recriar o `lab.db`, por isso ficou como
achado separado.

## Validação

`demo/verify.py` sobe as duas versões em portas efêmeras, com banco temporário,
e compara status **e** corpo da resposta:

| Caso | `app.py` | `app_fixed.py` |
|---|---|---|
| credencial válida | 200 | 200 |
| senha errada | 401 | 401 |
| bypass `' OR '1'='1' --` | 200 | 401 |
| comentário `admin'--` | 200 | 401 |
| bypass no campo senha | 200 | 401 |

Resultado: **comportamento esperado nos 5 casos**. O mesmo teste roda no GitHub
Actions a cada push.

## Fora de escopo

- Senhas em texto puro (`SEED` e `init_db`) — segundo defeito, deixado de
  propósito para um exercício de hashing e comparação em tempo constante.
- Ausência de sessão, cookie e CSRF.
- Limite de tamanho do `Content-Length`.
- Qualquer teste fora de `127.0.0.1`.
