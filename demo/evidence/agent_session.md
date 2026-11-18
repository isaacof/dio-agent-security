# Sessão com o agente

Registro da análise do `demo/app.py` conduzida pelo DIO Agent com a skill
`vulnerability-analysis` carregada.

## Como esta sessão foi executada

- Harness: **OpenCode**, que lê o `AGENTS.md` da pasta do projeto.
- Modelo: `opencode/deepseek-v4.1-flash-free`.
- Data: 17/11/2026.
- O agente leu, nesta ordem: `AGENTS.md`, `agent/persona.md`,
  `agent/knowledge/security-basics.md`, `skills/vulnerability-analysis/SKILL.md`
  e o alvo `demo/app.py`.
- As respostas do estudante (turno 2 e turno 3) fazem parte do cenário de
  demonstração. Nenhum comando foi executado pelo agente; ele só leu arquivos.

> **Nota sobre os números de linha.** A sessão foi conduzida sobre a versão
> anterior do laboratório, sem o CSS e sem o bloco que exibe a consulta na
> página. A falha é a mesma, mas o arquivo cresceu e os números citados na
> conversa mudaram. As referências atuais estão em
> [`docs/relatorio-sqli.md`](../../docs/relatorio-sqli.md), que foi atualizado
> depois do redesenho. O texto da conversa ficou como foi produzido.

O mesmo `AGENTS.md` é lido pelo Hermes e pelos demais harnesses compatíveis. O
que muda é a sala; o mentor é o mesmo.

---

## Turno 1 — pedido

> Analise o demo/app.py como especialista em AppSec. Quero entender a falha, o
> impacto e como corrigir.

### Resposta

Li os quatro arquivos e o `demo/app.py` (151 linhas). Antes de classificar
risco, aqui está o que consegui confirmar no arquivo.

**O que já verifiquei**

- **Linhas 73–76:** `authenticate()` monta a consulta por concatenação —
  `f"WHERE username = '{username}' AND password = '{password}'"` — com os
  valores vindos do formulário (linhas 110–111). É o padrão clássico de
  injeção de SQL.
- **Linhas 28–32 e 57:** senhas em texto puro e o próprio docstring avisa que
  é intencional.
- **Linhas 119–122:** a saída usa `html.escape()`, então o XSS refletido nesse
  ponto está tratado.
- **Linhas 114–117:** falha de login devolve mensagem genérica — não confirma
  se o usuário existe.
- **Linhas 129 e 137:** bind padrão em `127.0.0.1`, e `--host` permite mudar.
- **Não verifiquei** nada em execução: não subi o servidor, não testei entrada
  nenhuma e não há confirmação de que a consulta devolve mais de uma linha (o
  código usa `fetchone()`).

**Lacunas que o arquivo não responde**

O docstring diz "laboratório", mas eu não presunço isso: arquivo pode ser
copiado para qualquer lugar.

**Bloco A — onde roda** (define se a falha é exercício ou incidente)
- Esse código é seu, de um laboratório montado por você, ou de algo em uso?
- Onde ele executa: sua máquina, contêiner, VM, servidor com IP público?
- Tem autenticação, VPN ou proxy na frente? Quem consegue chegar no `/login`?

**Bloco B — o que ele protege** (define o impacto real, não o teórico)
- Além do `lab.db` local, esse banco guarda dado de alguém — pessoal,
  financeiro, credencial reaproveitada?
- Existe backup ou o dado é descartável? Se o banco for zerado, perde algo?

**Bloco C — o que já se sabe** (define prazo e se o estojo ainda está em jogo)
- Isso veio de scanner, de suspeita sua ou de algo já acontecido?
- Já existe versão corrigida rodando em algum ambiente?
- Há prazo ou dependência externa (entrega de desafio, apresentação, outra
  pessoa usando o arquivo)?

Se não souber responder algum item, tudo bem — sigo com o que houver e
registro a lacuna, em vez de inventar contexto.

Uma última coisa antes de você responder: no seu entendimento, por que
concatenar texto na consulta é diferente de "escapar os caracteres"?

---

## Turno 2 — contexto e análise completa

> **Estudante:** é meu, é um laboratório que eu montei para estudar. Roda na
> minha máquina, em 127.0.0.1, sem exposição para a internet, sem VPN nem
> proxy. A própria tela de login é o único acesso.
>
> Só o lab.db que o próprio app cria, com três usuários fictícios (admin,
> alice, bob). Dado descartável, sem backup, nada de pessoa real.
>
> Não veio de scanner nem de incidente. Estou estudando e quero entender o
> padrão. Não existe versão em produção. Sem prazo.
>
> Sobre a sua pergunta: concatenar deixa o texto digitado virar parte do
> comando; escapar tenta neutralizar caracteres especiais, mas continua
> montando comando. Escapar depende de o programador acertar todos os casos, e
> um contexto diferente (número, LIKE, ORDER BY) quebra a proteção.
> Parametrizar mantém a estrutura fixa e manda o valor separado.

### Resposta

Boa resposta na pergunta sobre escape — você acertou o ponto central: escape
tenta consertar o dado, parametrização separa dado de comando. Vamos fechar.

**Resumo**

- **Falha:** SQL Injection no login, por concatenação de string
- **CWE:** CWE-89 (Improper Neutralization of Special Elements used in an SQL
  Command). **OWASP Top 10 2021:** A03 Injection. **ATT&CK:** T1190 aplica-se a
  aplicação exposta à internet — no seu cenário (localhost) eu não usaria esse
  rótulo, ele inflaria o risco
- **Impacto:** Alto (latente) — a falha permite ler e alterar a tabela `users`
  e autenticar sem senha. No cenário atual o dado é fictício e descartável,
  então o impacto *material hoje* é Baixo; o que justifica tratar é o padrão,
  que você vai reusar
- **Probabilidade:** Baixa — bind em `127.0.0.1` (linha 137), sem exposição,
  exige acesso à sua máquina
- **Severidade:** Média (Alto × Baixa)
- **Prazo sugerido:** próxima janela — na prática, antes de copiar esse padrão
  para qualquer outro projeto

**Evidência**

Linhas 73–76 montam a consulta com `f"..."`; linhas 110–111 trazem os valores
do formulário. **Verificado no arquivo.** **Não verificado:** execução,
resultado do payload, e qual linha o `fetchone()` devolve. Curiosidade útil: o
próprio arquivo já usa `?` corretamente no `INSERT` (linha 66) — a forma segura
está ali, três funções acima.

**Como a falha funciona**

Entrada: `username` do POST. Sink: `conn.execute(query)`. Payload mínimo de
laboratório, no campo usuário:

```text
' OR '1'='1' --
```

O `'` fecha a string; `OR '1'='1'` torna a condição sempre verdadeira; `--`
comenta o resto, anulando a checagem de senha. **Inferência** (não executei):
retorna a primeira linha da tabela, provavelmente `admin` pela ordem de `id`, e
o app responde "Bem-vindo, admin".

O que **não** permite: o driver executa um único statement, sem empilhar
comandos; não dá shell nem derruba o serviço. E `fetchone()` limita a uma linha
por vez.

**Correção**

**Causa raiz:** a consulta é montada com o valor, então a entrada muda a
estrutura do comando.

O agente propôs aqui uma correção mais ampla, com `pbkdf2_hmac`, salt por
usuário e comparação em tempo constante, além de limite de tentativas. Essa é a
direção correta para produção, mas vai além da correção mínima do exercício.
No `app_fixed.py` foi aplicada apenas a consulta parametrizada, mantendo o
schema atual; o hashing ficou registrado como achado separado.

**Defesa em profundidade:** bind explícito em `127.0.0.1` (ou remover
`--host`); limite de tentativas por IP e por usuário; log de falha sem senha;
mensagem genérica — essa você já tem (linha 115); teste automatizado cobrindo o
payload.

**Efeito colateral:** exige migrar o schema (`password_hash`, `salt`) e recriar
o `lab.db`; o seed atual para de funcionar; e o payload deixa de "funcionar" —
para continuar estudando, mantenha a versão vulnerável em outro arquivo.

**Validação**

Mesmo payload deve cair em "Credenciais invalidas".

**Fora de escopo**

Senhas em texto puro (linhas 28–32, 57) e ausência de sessão/CSRF — achados
reais, mas separados deste. XSS na resposta já está tratado com `html.escape`.

---

## Turno 3 — validação no arquivo corrigido

> **Estudante:** apliquei a correção mínima em `demo/app_fixed.py`: consulta
> parametrizada, mantendo o schema atual de propósito. Também escrevi
> `demo/verify.py`. Valide.

### Resposta

**O que verifiquei no arquivo**

`authenticate()` em `app_fixed.py` (linhas 76–80) usa `?` com tupla de
parâmetros: estrutura fixa, valor como dado. Percorri os três `execute()` do
arquivo — `CREATE` (62–63), `INSERT` (67) e `SELECT` (77–78) — e **nenhum**
interpola string. A mitigação está no ponto certo e não deixou o mesmo padrão
em outro lugar.

Detalhe que funcionou por sorte sua, não por acaso: `DB_PATH` é lido no import
(linha 28), e `verify.py` define `LAB_DB` **antes** dos imports. Se essa ordem
invertesse, o teste rodaria contra o seu `lab.db` real. Vale um comentário ali.

**O que o teste cobre**

Bom desenho: controle positivo (`admin/admin123` → 200), controle negativo
(senha errada → 401) e dois payloads. O controle positivo é o que impede a
conclusão falsa de "tudo retorna 401, então está seguro". Servidor em porta
efêmera, banco temporário, `shutdown()` no `finally`, código de saída diferente
de zero em falha. **Isso prova o que você queria provar** — mesmo payload,
resultados opostos.

**O que ficou de fora**

1. **Asserta só o status, não o corpo.** Um 200 com página de erro passaria.
2. **Payload só no campo usuário.** Em `app.py` o campo senha também é sink.
3. Não valida o estado do banco depois (nenhuma linha alterada).
4. Sem teste de limite de tentativas, `--host` exposto ou log.
5. O sucesso do teste prova **um** sink fechado, não que o app é seguro.

**Veredito**

**Correção: correta** [verificado por leitura]. **Validação: procedente,
pendente de execução** — não rodei nada, então o resultado é expectativa, não
evidência. Rode o `verify.py` e traga a saída.

Fechando: `(not ok_v) + (not ok_f)` funciona porque `bool` soma como 1 em
Python — mas confunde quem lê. Prefira `failures += int(not ok_v) + int(not ok_f)`.

Qual foi o raciocínio que você leva dessa análise — e o que você olharia
primeiro no próximo `execute()` que encontrar?

### O que foi ajustado depois

Os quatro pontos acionáveis foram aplicados em `verify.py`:

- teste passou a conferir o corpo da resposta, não só o status;
- caso novo com o payload no campo senha (5 casos no total);
- `failures += int(...)`, em vez de somar booleanos;
- comentário explicando por que `LAB_DB` é definido antes do import.

Saída real depois do ajuste, em
[`verify_output.txt`](verify_output.txt): **comportamento esperado nos 5 casos**.

---

## Comparação: a mesma pergunta sem a skill

O mesmo pedido foi enviado a um chat genérico, sem `AGENTS.md`, sem persona e
sem a skill. O resultado, em resumo:

| Aspecto | Com a skill | Chat genérico |
|---|---|---|
| Primeira ação | Leu o código e pediu o contexto em três blocos | Entregou a análise completa de imediato |
| Classificação | CWE-89, OWASP A03, e recusou T1190 por não haver exposição | CWE-89, OWASP A03, vários vetores |
| Risco | Impacto Alto × Probabilidade Baixa = Severidade Média, com prazo | Descreveu impacto, sem matriz e sem prazo |
| Exploração | Um payload mínimo, com o que a falha **não** permite | Payload de bypass, `UNION SELECT` e time-based de uma vez |
| Correção | Causa raiz, correção mínima, defesa em profundidade, efeito colateral | Lista de cinco itens, incluindo migrar para Flask/Django |
| Validação | Propôs teste e pediu confirmação | Não pediu validação |
| Fechamento | Perguntou o que o estudante aprendeu | Encerrou na resposta |

O chat genérico não errou o diagnóstico. Errou o processo: tratou como
produção um arquivo de laboratório, entregou três vetores de uma vez e não
mediu risco. A skill existe para impedir isso.
