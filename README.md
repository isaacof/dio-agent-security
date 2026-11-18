# DIO Agent — especializado em análise de vulnerabilidades

Evolução do [DIO Agent](https://github.com/digitalinnovationone/dio-agent)
para um mentor de segurança de aplicação: em vez de responder direto, o agente
entende o contexto, classifica a falha, mede impacto e probabilidade, orienta a
correção e valida o resultado.

> Este repositório parte do projeto base da DIO. A especialização está na skill
> `vulnerability-analysis`, no arquivo `agent/knowledge/security-basics.md` e nos
> ajustes de persona e `AGENTS.md`. Nada de modelo treinado: o comportamento
> vem dos arquivos em Markdown.

## 1. A especialização, e por quê

O DIO Agent original é um mentor de estudos. Ele sabe montar plano de estudos,
destravar desafio e revisar portfólio — mas não tem processo para analisar
código inseguro. Se alguém pede "olha esse login", a resposta tende a ser
genérica: "use consulta parametrizada".

O problema não é a resposta estar errada. É ela vir antes do contexto. A mesma
falha muda de gravidade conforme onde o código roda:

- um SQL Injection num script local de estudo é um exercício;
- o mesmo SQL Injection no login de um servidor exposto, com dado de cliente,
  é incidente com prazo.

Por isso a especialização tem três partes:

| Parte | Papel |
|---|---|
| **Processo** (`skills/vulnerability-analysis/`) | Sete etapas fixas, da coleta de contexto à validação da correção |
| **Vocabulário** (`agent/knowledge/security-basics.md`) | Vulnerabilidade, ameaça e risco, tríade CIA, superfície de ataque, projeto seguro |
| **Postura** (`agent/persona.md` e `AGENTS.md`) | Investigar antes de opinar, falar em evidência, calibrar risco, recusar alvo de terceiros |

## 2. Arquivos criados e alterados

| Arquivo | Tipo | O que faz |
|---|---|---|
| `skills/vulnerability-analysis/SKILL.md` | **criado** | O roteiro que o agente segue: enquadrar, reunir evidência, classificar (CWE/ATT&CK/OWASP), avaliar risco, explicar a exploração, corrigir e validar |
| `skills/vulnerability-analysis/README.md` | **criado** | Explica a skill para pessoas: etapas, matriz de severidade, limites |
| `agent/knowledge/security-basics.md` | **criado** | Base conceitual: vulnerabilidade × ameaça × risco, CIA, autenticação × autorização, validação × codificação de saída, princípios de projeto seguro |
| `agent/persona.md` | alterado | Nova seção **Modo AppSec**: como o agente pensa e fala em segurança |
| `AGENTS.md` | alterado | Linha da skill na tabela, item da base de conhecimento, regra 10 (perguntar antes de comandar) e limite de ambiente autorizado |
| `demo/app.py` | criado | Login vulnerável a SQL Injection, em Python puro |
| `demo/app_fixed.py` | criado | O mesmo login com consulta parametrizada |
| `demo/verify.py` | criado | Prova, por HTTP, que o bypass funciona em uma versão e falha na outra |
| `demo/README.md` | criado | Explica o laboratório e o que observar |
| `demo/evidence/` | criado | Saída real da verificação e transcrição da sessão com o agente |
| `README.md` | alterado | Este arquivo |

### A skill em sete etapas

1. **Enquadrar o alvo** — onde roda, quem alcança, quais dados toca.
2. **Reunir evidência** — trecho de código, configuração, versões, erro.
3. **Identificar e classificar** — CWE, MITRE ATT&CK, OWASP Top 10.
4. **Avaliar** — impacto, probabilidade e severidade por matriz.
5. **Explicar a exploração** — payload mínimo em laboratório e o que a falha
   *não* permite.
6. **Orientar a correção** — causa raiz, correção mínima, defesa em
   profundidade, efeito colateral.
7. **Validar** — repetir o payload, rodar o teste, procurar o mesmo padrão em
   outros pontos.

Detalhe importante: a skill não tem resposta pronta. Ela define perguntas,
ordem e formato. O conteúdo sai do código que o estudante enviar.

## 3. A melhoria escolhida

Entre as ideias sugeridas, escolhi **fazer a análise sair sempre no mesmo
formato**, com impacto, probabilidade e severidade. Motivo: sem formato fixo,
dois casos analisados no mesmo dia saem incomparáveis — um vira parágrafo, o
outro vira lista, e ninguém consegue priorizar.

A matriz usada é qualitativa, inspirada em avaliação de risco:

| Impacto \ Probabilidade | Alta | Média | Baixa |
|---|---|---|---|
| **Alto** | Crítica | Alta | Média |
| **Médio** | Alta | Média | Baixa |
| **Baixo** | Média | Baixa | Informativa |

O agente também declara o prazo sugerido de correção por severidade: Crítica e
Alta antes de produção; Média na próxima janela; Baixa e Informativa no
backlog. Isso aproxima a conversa do que um time faz na prática — e abre
caminho para a ideia de DevSecOps, com a mesma ficha aplicada a cada alteração
antes do deploy.

## 4. Como rodar

### Com Hermes

Instale o Hermes conforme a documentação oficial:
https://hermes-agent.nousresearch.com/docs

Depois, sempre **na pasta do projeto** — é isso que faz o agente encontrar
`AGENTS.md`, a persona, o conhecimento e as skills:

```bash
git clone https://github.com/isaacof/dio-agent-security.git
cd dio-agent-security
hermes
```

Se abrir o Hermes em outra pasta, ele não vê estes arquivos e responde como um
chat comum.

### Com outro harness

Qualquer harness que leia `AGENTS.md` funciona: Claude Code, Codex, OpenCode,
Antigravity. Abra a pasta do projeto — a que contém o `AGENTS.md` — e converse.

### Teste rápido

```bash
cd demo
python verify.py
```

O script sobe as duas versões do login em `127.0.0.1`, em portas efêmeras, e
compara as respostas. Saída esperada:

```text
[credencial valida]        app.py 200 | app_fixed.py 200
[senha errada]             app.py 401 | app_fixed.py 401
[bypass OR 1=1]            app.py 200 | app_fixed.py 401
[comentario apos usuario]  app.py 200 | app_fixed.py 401
[bypass no campo senha]    app.py 200 | app_fixed.py 401
```

### Conversa de exemplo

```text
Analise o demo/app.py como especialista em AppSec.
Quero entender a falha, o impacto e como corrigir.
```

O esperado é o agente perguntar o contexto antes de sugerir qualquer coisa.
A transcrição real está em
[`demo/evidence/agent_session.md`](demo/evidence/agent_session.md), e a saída
do teste em [`demo/evidence/verify_output.txt`](demo/evidence/verify_output.txt).

## 5. Resultado da análise

Resumo do que a skill produz para o `demo/app.py`:

| Campo | Valor |
|---|---|
| Falha | SQL Injection na autenticação, por concatenação de string |
| CWE | CWE-89 |
| OWASP Top 10 | A03:2021 Injection |
| MITRE ATT&CK | T1190 só se a aplicação estiver exposta; em `127.0.0.1` não se aplica |
| Impacto | Alto em potencial (bypass de login e leitura da tabela `users`); baixo no material atual, que é fictício e descartável |
| Probabilidade | Baixa no laboratório: bind em `127.0.0.1`, sem exposição |
| Severidade | Média (Alto × Baixa) no laboratório; sobe para Crítica se o padrão for reutilizado em serviço exposto |
| Prazo sugerido | Antes de reutilizar o padrão em qualquer outro projeto |
| Correção | Consulta parametrizada, com defesa em profundidade |
| Validação | `verify.py` confirma os cinco casos; o mesmo payload autentica em `app.py` e é recusado em `app_fixed.py` |

O laboratório usa dado fictício e roda só em `127.0.0.1`. A versão `app.py`
existe para ser estudada, não usada.

## 6. Estrutura do repositório

```text
dio-agent/
├── AGENTS.md                     definição do agente (lida pelo harness)
├── agent/
│   ├── persona.md                personalidade, com a seção Modo AppSec
│   └── knowledge/
│       ├── dio-platform.md
│       ├── learning-experiences.md
│       └── security-basics.md    vocabulário de segurança
├── skills/
│   ├── vulnerability-analysis/   a skill nova
│   │   ├── SKILL.md
│   │   └── README.md
│   ├── study-plan/
│   ├── unblock-challenge/
│   ├── explain-concept/
│   ├── web-search/
│   ├── portfolio-review/
│   └── ai-builder-path/
└── demo/                         laboratório de SQL Injection
    ├── app.py
    ├── app_fixed.py
    ├── verify.py
    ├── README.md
    └── evidence/
```

## 7. Skills disponíveis

| Skill | Para que serve | Arquivo |
|---|---|---|
| Análise de vulnerabilidade | Analisa falha, risco e correção com contexto | [`skills/vulnerability-analysis/SKILL.md`](skills/vulnerability-analysis/SKILL.md) |
| Plano de estudos | Organiza o que estudar, em que ordem e em quanto tempo | [`skills/study-plan/SKILL.md`](skills/study-plan/SKILL.md) |
| Destravar desafio | Conduz até a solução sem entregar a resposta | [`skills/unblock-challenge/SKILL.md`](skills/unblock-challenge/SKILL.md) |
| Explicar conceito | Explica com analogia e exemplo curto | [`skills/explain-concept/SKILL.md`](skills/explain-concept/SKILL.md) |
| Pesquisa na web | Responde com fonte citada o que muda com o tempo | [`skills/web-search/SKILL.md`](skills/web-search/SKILL.md) |
| Revisão de portfólio | Feedback sobre GitHub e portfólio antes da vaga | [`skills/portfolio-review/SKILL.md`](skills/portfolio-review/SKILL.md) |
| Caminho AI Builder | Próximo passo na Carreira AI Builder | [`skills/ai-builder-path/SKILL.md`](skills/ai-builder-path/SKILL.md) |

## 8. Limites

- A skill vale para código e laboratório do próprio estudante.
- O agente não testa sistema de terceiros, não pede credencial e não entrega
  exploit voltado para alvo real.
- O laboratório usa banco local, porta local e usuários fictícios.
- As senhas do laboratório ficam em texto puro de propósito, como segundo
  defeito para um exercício separado.

## 9. Créditos

Projeto base: [digitalinnovationone/dio-agent](https://github.com/digitalinnovationone/dio-agent).
Esta é uma especialização independente, feita para o desafio da DIO.
