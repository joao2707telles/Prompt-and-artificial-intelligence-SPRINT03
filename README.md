
# EV Challenge — GoodWe

## Sprint 03 — Agentes de IA e Evolução Conversacional

Projeto desenvolvido para a disciplina de Prompt and Artificial Intelligence
do curso de Ciência da Computação da FIAP.

## GoodWezinho

O GoodWezinho é um chatbot voltado para usuários de veículos elétricos
e interessados nos carregadores da linha HCA G2 da GoodWe.

O projeto foi desenvolvido inicialmente nas Sprints 1 e 2 e foi
refatorado na Sprint 03 utilizando um framework de agentes de IA.

## Evolução da Sprint 03

Nas versões anteriores, o fluxo conversacional era controlado
manualmente pelo código.

Na Sprint 03, a aplicação passou a utilizar LangGraph para:

- controlar o fluxo conversacional;
- gerenciar memória por sessão;
- aplicar guardrails;
- controlar diferentes rotas de resposta;
- integrar o RAG à arquitetura do agente.

## Tecnologias utilizadas

- Python
- Google Colab
- LangGraph
- LangChain
- Gemini API
- Gemini 3.5 Flash
- Gemini 3.5 Flash-Lite
- RAG
- InMemoryVectorStore
- Google Generative AI Embeddings

## Funcionalidades

O GoodWezinho é capaz de:

- responder dúvidas sobre os carregadores HCA G2;
- consultar informações do datasheet oficial através de RAG;
- identificar veículos presentes na base do projeto;
- calcular o custo estimado de uma carga completa;
- estimar o tempo de carregamento;
- manter memória durante a sessão;
- resistir a tentativas de Prompt Injection;
- bloquear orientações elétricas potencialmente perigosas;
- evitar aconselhamento jurídico e financeiro inadequado;
- evitar inventar especificações técnicas.

## Memória conversacional

A memória é implementada utilizando o recurso InMemorySaver
do LangGraph.

Cada conversa possui um thread_id próprio, permitindo que o agente
recupere informações mencionadas anteriormente na mesma sessão.

Exemplo utilizado nos testes:

1. O usuário informa que possui um BYD Dolphin Mini.
2. Pergunta o custo de uma carga completa.
3. Pergunta quanto tempo demora para carregar.

O agente recupera o veículo mencionado no primeiro turno sem exigir
que o usuário repita a informação.

## RAG

O projeto utiliza o datasheet do carregador GoodWe HCA G2 como
base de conhecimento.

O documento é:

1. carregado;
2. dividido em chunks;
3. transformado em embeddings;
4. armazenado em um InMemoryVectorStore;
5. consultado através de similarity search.

Os trechos mais relevantes são fornecidos ao modelo antes da resposta.

## Segurança

Foram implementados testes de:

- Prompt Injection;
- segurança elétrica;
- aconselhamento jurídico;
- aconselhamento financeiro;
- tentativa de induzir especificações inventadas.

Prompt Injection e solicitações elétricas perigosas podem ser
interceptadas diretamente pelo fluxo do LangGraph antes da chamada
ao modelo de linguagem.

## Comparação entre modelos

Foram avaliados:

- Gemini 3.5 Flash
- Gemini 3.5 Flash-Lite

Resultados médios observados:

| Modelo | Latência média | Tokens registrados |
|---|---:|---:|
| Gemini 3.5 Flash | 9,09 s | 9.771 |
| Gemini 3.5 Flash-Lite | 0,81 s | 7.275 |

Os dois modelos apresentaram comportamento adequado nos testes
funcionais, de memória e segurança.

O Gemini 3.5 Flash-Lite foi selecionado para a versão final por
apresentar menor latência e menor utilização de tokens nos testes
registrados, sem perda relevante de qualidade.

## Estrutura principal

```text
agent.py
prompts.py
goodwe_tools.py
rag.py
relatorio_modelos.md
resultados_modelos.csv
integrantes.txt
requirements.txt
tests/
