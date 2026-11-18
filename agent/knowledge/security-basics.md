# Fundamentos de segurança

Contexto base para o agente conversar sobre segurança sem improvisar. Não é um
curso: é o vocabulário mínimo para conduzir uma análise e não confundir os
conceitos.

## 1. Vulnerabilidade, ameaça e risco

Os três termos são usados como sinônimos no dia a dia, mas significam coisas
diferentes. A distinção muda a recomendação.

| Termo | Definição | Exemplo |
|---|---|---|
| **Vulnerabilidade** | Uma fraqueza concreta no sistema | Login monta SQL por concatenação |
| **Ameaça** | Quem ou o que pode explorar a fraqueza | Atacante automatizado que varre a internet |
| **Risco** | A combinação entre probabilidade e impacto | Conta de admin exposta e sem MFA |

Uma vulnerabilidade sem ameaça relevante e sem impacto continua sendo um
defeito, mas o risco pode ser baixo. Isso justifica priorizar: nem todo achado
merece parar a entrega.

## 2. A tríade CIA

| Propriedade | O que protege | Pergunta de teste | Falha típica |
|---|---|---|---|
| **Confidencialidade** | Quem pode ler | "Quem consegue ver esse dado sem permissão?" | SQL Injection que devolve dados de outros usuários |
| **Integridade** | Quem pode alterar | "Quem consegue mudar esse dado sem autorização?" | Mass assignment que permite virar admin |
| **Disponibilidade** | Quem consegue usar | "O que derruba esse serviço?" | Endpoint sem limite que esgota o banco |

Uma falha pode atingir mais de uma propriedade. Classifique cada uma
separadamente antes de somar o impacto.

## 3. Superfície de ataque

É tudo que um atacante consegue alcançar sem privilégio: formulários, APIs,
parâmetros de URL, cabeçalhos, uploads, portas abertas, credenciais vazadas.
Reduzir superfície é mais barato do que corrigir cada falha.

Perguntas úteis:

- O endpoint precisa estar exposto para a internet?
- Precisa aceitar o formato que aceita?
- Precisa devolver o detalhe que devolve?

## 4. Autenticação e autorização

- **Autenticação** responde "quem é você". Falhas comuns: senha fraca sem
  limite de tentativas, sessão que não expira, recuperação de senha previsível.
- **Autorização** responde "o que você pode fazer". Falha comum: conferir o
  papel do usuário na interface e não no servidor (IDOR, escalada horizontal).

Regra prática: toda operação no servidor confere permissão, mesmo que a
interface já esconda o botão.

## 5. Validação de entrada e codificação de saída

- **Validação** rejeita o que não faz sentido para o campo: tipo, tamanho,
  formato, faixa.
- **Codificação de saída** trata o dado conforme o destino: SQL usa consulta
  parametrizada, HTML usa escape, shell usa lista de argumentos, caminho de
  arquivo usa normalização e allowlist.

Validar a entrada não substitui tratar o destino. As duas camadas resolvem
problemas diferentes.

## 6. Princípios de projeto seguro

| Princípio | Aplicação |
|---|---|
| Menor privilégio | Conta do banco sem permissão de DDL; processo sem root |
| Padrão seguro | Negar por padrão, exigir configuração explícita para abrir |
| Defesa em profundidade | Mais de uma barreira para a mesma falha |
| Falhar fechado | Em erro de verificação, negar acesso |
| Simplicidade | Menos código no caminho crítico, menos falha |
| Segredos fora do código | Variável de ambiente ou cofre, nunca no repositório |
| Atualização | Dependência e sistema com patch aplicado |

## 7. Dados e privacidade

- Colete o mínimo necessário e guarde pelo tempo necessário.
- Dado pessoal exige controle de acesso e registro de quem acessou.
- Log não é depósito de dado sensível: senha, token e documento não vão para o
  log.
- Em laboratório, use dado fictício. Nunca copie base real para testar.

## 8. Registro e monitoramento

Log útil para segurança responde: quem, quando, de onde, o que tentou e qual
foi o resultado. Falhas de autenticação, mudanças de permissão e erros de
autorização são os eventos que mais rendem detecção.

Sem telemetria, uma falha pode estar sendo explorada há meses sem ninguém
notar. Detecção depende de dado coletado antes do incidente.

## 9. Referências de estudo

- **OWASP Top 10** — riscos mais comuns em aplicações web.
- **OWASP ASVS** — requisitos verificáveis de segurança de aplicação.
- **CWE** — catálogo de fraquezas de software, com identificador por tipo.
- **MITRE ATT&CK** — táticas e técnicas usadas por atacantes.
- **NIST SP 800-61** — ciclo de resposta a incidente.
- **NIST SSDF** — práticas de desenvolvimento seguro.

Os identificadores e as versões dessas referências mudam. Ao citar um número,
confira na fonte oficial em vez de repetir de memória.

## 10. O que o agente faz com isso

- Usa o vocabulário correto ao classificar um achado.
- Não trata vulnerabilidade como risco sem avaliar impacto e probabilidade.
- Lembra que correção é causa raiz mais validação, não paliativo.
- Recusa analisar alvo de terceiros e não pede credencial.
