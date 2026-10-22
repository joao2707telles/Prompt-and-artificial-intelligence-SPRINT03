# EV Challenge — GoodWe  
## Sprint 04 — Avaliação Sistemática do Agente

### 1. Introdução

A Sprint 04 tem como objetivo avaliar de forma automática o desempenho do chatbot desenvolvido nas sprints anteriores do projeto EV Challenge — GoodWe.

Nas Sprints 1 e 2 foram definidos o problema, o contexto do chatbot, os testes iniciais e sua implementação. Na Sprint 3 o agente foi reorganizado utilizando LangGraph, memória por sessão, RAG e regras de segurança.

Nesta sprint foi desenvolvido um pipeline de avaliação para substituir parte da análise manual realizada anteriormente por uma avaliação automática e reproduzível.

---

### 2. Golden Dataset

Foi criado um golden dataset com 13 casos de teste. As perguntas foram escolhidas para representar diferentes situações que o chatbot pode receber.

As categorias utilizadas foram:

- Funcionalidade;
- Escopo;
- Segurança;
- Prompt Injection;
- Segurança elétrica;
- Questões jurídicas e financeiras;
- Caso de borda;
- Memória da conversa.

Cada teste possui uma pergunta e um critério de aceite que descreve o comportamento esperado do agente.

Também foi incluído um teste de múltiplos turnos para verificar se a memória por sessão implementada na Sprint 3 continua funcionando corretamente.

---

### 3. Pipeline de avaliação

O pipeline foi desenvolvido em Python e executa automaticamente os casos presentes no golden dataset.

Foram avaliadas duas versões do agente utilizadas durante a Sprint 3:

- Flash;
- Flash-Lite.

Para cada versão, o pipeline envia as perguntas ao agente e armazena suas respostas.

Depois, um segundo modelo é utilizado como **LLM as a Judge**, recebendo a pergunta, a resposta produzida pelo agente e o critério de aceite.

O juiz automático atribui notas para cada resposta e os resultados são armazenados em arquivos CSV.

Os arquivos gerados pelo pipeline são:

- `resultados_detalhados.csv`;
- `resumo_metricas.csv`.

---

### 4. Métricas utilizadas

Foram utilizadas as seguintes métricas:

**Correção:** verifica se a resposta atende corretamente ao critério de aceite.

**Aderência ao escopo:** verifica se o chatbot continua focado em GoodWe, mobilidade elétrica e carregamento de veículos elétricos.

**Fidelidade:** verifica se o agente evita inventar informações e respeita o contexto disponível.

**Segurança:** utilizada nos casos envolvendo Prompt Injection, risco elétrico, informações incorretas e questões jurídicas ou financeiras.

**Taxa de recusa correta:** verifica se o agente recusou corretamente solicitações que deveriam ser bloqueadas.

Cada métrica principal recebe uma nota de 0 a 5. O score final é calculado utilizando a média das métricas aplicáveis ao teste.

---

### 5. Resultados

A tabela abaixo apresenta os resultados obtidos pelo pipeline.

| Métrica | Flash | Flash-Lite |
|---|---:|---:|
| Correção média | PREENCHER | PREENCHER |
| Aderência ao escopo | PREENCHER | PREENCHER |
| Fidelidade | PREENCHER | PREENCHER |
| Segurança | PREENCHER | PREENCHER |
| Taxa de recusa correta | PREENCHER | PREENCHER |
| Score final | PREENCHER | PREENCHER |

Os valores acima serão obtidos diretamente pelo arquivo `resumo_metricas.csv` gerado pelo pipeline.

---

### 6. Classificação das versões

Após a execução completa do pipeline, a versão com maior score final será considerada a versão com melhor desempenho geral.

Além do score final, serão analisadas separadamente as métricas de correção, fidelidade, segurança e aderência ao escopo para evitar que a decisão seja baseada em apenas um valor.

**Versão com melhor desempenho:** PREENCHER APÓS EXECUÇÃO.

---

### 7. Comparação com a avaliação manual da Sprint 3

Na Sprint 3, os modelos foram comparados manualmente através de testes de funcionamento, segurança e comportamento do agente.

A Sprint 04 permite comparar essa análise manual com uma avaliação automática baseada em critérios iguais para todas as respostas.

Após a execução do pipeline será possível verificar se o resultado automático confirma a conclusão obtida anteriormente ou se existem diferenças entre as duas formas de avaliação.

**Resultado da comparação:** PREENCHER APÓS EXECUÇÃO.

---

### 8. Limitações

Uma das limitações observadas foi o limite de requisições da API utilizada durante os testes.

Como cada versão do agente precisa responder diversas perguntas e as respostas também precisam ser avaliadas pelo LLM juiz, o número de requisições pode aumentar rapidamente.

Outra limitação é que a avaliação utiliza um modelo de linguagem como juiz. Mesmo utilizando o mesmo critério para todas as respostas, ainda pode existir alguma variação ou interpretação diferente do modelo avaliador.

Além disso, o golden dataset possui um número limitado de casos e não representa todas as perguntas possíveis que um usuário poderia fazer.

---

### 9. Conclusão

A Sprint 04 adicionou uma etapa de avaliação sistemática ao chatbot desenvolvido durante o semestre.

O golden dataset e o pipeline permitem testar diferentes versões do agente utilizando os mesmos critérios e gerar métricas comparáveis automaticamente.

Dessa forma, a escolha da melhor versão deixa de depender apenas de observação manual e passa a ser apoiada também por resultados quantitativos.

---

### 10. Equipe e divisão de trabalho

**Guilherme Figueira Velloso — RM 568827**  
Participação na revisão do golden dataset e validação dos casos de teste.

**José Augusto Ribeiro Freire Manfrinato — RM 571151**  
Participação na revisão dos critérios de avaliação e organização dos resultados.

**Lais da Silva Dias — RM 569943**  
Participação na validação dos testes e revisão do relatório final.

**João Augusto Poloniato Telles — RM 571443**  
Implementação e integração do pipeline de avaliação e organização dos resultados.

**Thiago Soalheiro Diamantino — RM 569316**  
Participação na revisão dos testes e comparação entre as versões do agente.

**Kauan Damasceno de Lima — RM 573727**  
Participação na revisão da documentação e análise final dos resultados.
