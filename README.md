# Research Agent

Um agente de IA simples que responde perguntas — e que sabe quando precisa "parar pra pesquisar" antes de responder.

É um MVP pensado pra portfólio: dá pra entender o projeto inteiro em poucos minutos de leitura, mas ele já mostra na prática como um agente de verdade toma decisões usando LangGraph, chama ferramentas externas (tool calling) e gerencia contexto — sem cair em over-engineering nem em abstrações que só existem pra impressionar.

A ideia central é simples: você manda uma pergunta pra API, e quem decide se precisa consultar uma base de conhecimento antes de responder é o próprio modelo de linguagem — não um `if` procurando palavra-chave no meio do texto.

## Como funciona (arquitetura)

```text
Usuário
   │
   ▼
FastAPI  (POST /chat)
   │
   ▼
LangGraph
   │
   ▼
Agent  ──── o LLM decide: preciso de uma ferramenta pra responder isso?
   │
   ├── Não precisa ──────────────────────────────► responde direto
   │
   └── Precisa ──► Tool (search_knowledge_base) ──► resultado vira "contexto"
                                                          │
                                                          ▼
                                                   volta pro Agent, que
                                                   usa esse contexto pra
                                                   montar a resposta final
```

Na prática, isso é um grafo de estados do LangGraph com só dois nós (`agent` e `tool`) e um ciclo curto entre eles. O mesmo nó `agent` roda duas vezes quando a ferramenta é usada: uma pra decidir, outra pra responder já com o resultado da busca em mãos.

## Tecnologias

- **Python 3.12**
- **FastAPI** — a API em si, com documentação interativa automática
- **LangChain** — abstração sobre o modelo de linguagem e as ferramentas
- **LangGraph** — orquestração do fluxo do agente como um grafo de estados
- **Pydantic** — validação de entrada/saída da API
- **Google Gemini** — o LLM usado (via `langchain-google-genai`)
- **Docker** — pra rodar tudo sem precisar configurar ambiente na mão

## O que esse projeto demonstra

Foi construído pra ser mostrado numa entrevista, então cada peça existe por um motivo:

- **Integração com LLM** de verdade, via LangChain, sem hardcoding de prompt/resposta.
- **Engenharia de prompt** separada do código de negócio (`app/prompts/`), com instruções explícitas sobre quando usar a ferramenta e como diferenciar conhecimento próprio de informação buscada.
- **Fluxo de agente com LangGraph**, incluindo decisão condicional e um ciclo (agent → tool → agent).
- **Tool calling real** — quem decide chamar a ferramenta é o modelo (via `bind_tools`), não uma regra de palavras-chave no código.
- **Gerenciamento de estado e contexto**: o resultado da busca vira `AgentState.context`, e dá pra seguir esse dado passo a passo pelo código.
- **API bem estruturada**, com schemas tipados e documentação automática.

## Estrutura do projeto

```text
research-agent-ai/
├── app/
│   ├── main.py                  # monta a aplicação FastAPI
│   ├── config.py                # variáveis de ambiente (.env)
│   ├── api/
│   │   └── routes.py            # endpoint POST /chat
│   ├── agent/
│   │   ├── state.py             # AgentState (o que trafega no grafo)
│   │   ├── nodes.py             # agent_node e tool_node
│   │   ├── graph.py             # montagem do grafo com LangGraph
│   │   └── llm.py               # instância do modelo (Gemini)
│   ├── tools/
│   │   └── knowledge_base.py    # a tool search_knowledge_base
│   ├── prompts/
│   │   └── agent_prompt.py      # prompt de sistema do agente
│   └── schemas/
│       └── chat.py              # ChatRequest / ChatResponse
├── data/
│   └── knowledge_base.json      # base de conhecimento (7 documentos)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Como executar

### Com Docker (recomendado)

1. Copie o arquivo de variáveis de ambiente e preencha com sua chave:

   ```bash
   cp .env.example .env
   ```

   Você vai precisar de uma chave de API do Gemini — pode gerar de graça no [Google AI Studio](https://aistudio.google.com/). Coloque em `LLM_API_KEY` dentro do `.env`.

2. Suba tudo:

   ```bash
   docker compose up --build
   ```

3. A API sobe em `http://localhost:8003` (a porta interna do container continua sendo 8000 — o mapeamento `8003:8000` no `docker-compose.yml` só existe porque a 8000 já estava ocupada nesta máquina; sinta-se à vontade pra trocar de volta pra `"8000:8000"` se a sua estiver livre).

4. A documentação interativa fica em `http://localhost:8003/docs`.

### Sem Docker

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # e preencha LLM_API_KEY

uvicorn app.main:app --reload --port 8003
```

### Rodando os testes

```bash
pytest -v
```

Os testes usam um LLM "dublê" (fake), então rodam rápido e sem gastar chamadas de API de verdade.

## Exemplo de uso

Uma pergunta que exige consulta à base de conhecimento:

```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"O que é LangGraph?"}'
```

Resposta:

```json
{
  "answer": "Com base na base de conhecimento consultada, o LangGraph é uma biblioteca desenvolvida sobre o LangChain para orquestrar fluxos de agentes de IA utilizando grafos de estados...",
  "used_tool": true
}
```

E uma pergunta que o modelo consegue responder sozinho, sem precisar da ferramenta:

```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quanto é 15 + 27?"}'
```

```json
{
  "answer": "15 + 27 = 42.",
  "used_tool": false
}
```

## O que fica de fora de propósito

Esse é um MVP — não tem RAG com embeddings, banco vetorial, múltiplos agentes, autenticação, fila, cache distribuído nem observabilidade avançada. Tudo isso são evoluções possíveis, mas o objetivo aqui era ter algo pequeno o suficiente pra ler de ponta a ponta e entender exatamente o que cada parte faz.
