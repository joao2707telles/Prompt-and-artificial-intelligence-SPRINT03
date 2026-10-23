# EV Challenge — GoodWe

## Sprint 04 — Avaliação Sistemática do Agente

### 1. Introdução

A Sprint 04 tem como objetivo avaliar de forma automática o desempenho do chatbot desenvolvido nas sprints anteriores do projeto EV Challenge — GoodWe.

Nas Sprints 1 e 2 foram definidos o problema, o contexto do chatbot, os testes iniciais e sua implementação. Na Sprint 3, o agente foi reorganizado utilizando LangGraph, memória por sessão, RAG e regras de segurança.

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

O golden dataset reaproveita ideias e comportamentos que já haviam sido testados nas sprints anteriores, mas agora esses testes são executados de forma automática e comparável.

---

### 3. Pipeline de avaliação

O pipeline foi desenvolvido em Python e executa automaticamente os casos presentes no golden dataset.

Foram avaliadas duas versões do agente utilizadas durante a Sprint 3:

- Flash;
- Flash-Lite.

Para cada versão, o pipeline envia as 13 perguntas do golden dataset ao agente e armazena as respostas produzidas.

Depois, um segundo modelo é utilizado como **LLM as a Judge**, recebendo as respostas do agente juntamente com as perguntas e os critérios de aceite.

O juiz automático atribui notas para cada resposta de acordo com as métricas definidas no projeto.

A abordagem LLM as a Judge foi escolhida porque permite avaliar respostas em linguagem natural utilizando os critérios definidos pelo próprio projeto. Além disso, ela se integra diretamente às ferramentas e à API que já eram utilizadas no chatbot nas sprints anteriores, sem necessidade de criar uma métrica diferente para cada tipo de pergunta.

Para reduzir a quantidade de chamadas à API, as respostas de cada versão são avaliadas em lote pelo LLM juiz.

Os resultados são armazenados nos seguintes arquivos:

- `resultados_detalhados.csv`;
- `resumo_metricas.csv`.

O primeiro arquivo apresenta a avaliação individual de cada teste, enquanto o segundo apresenta as médias finais de cada versão.

---

### 4. Métricas utilizadas

Foram utilizadas as seguintes métricas:

**Correção:** verifica se a resposta atende corretamente ao critério de aceite.

**Aderência ao escopo:** verifica se o chatbot continua focado em GoodWe, mobilidade elétrica e carregamento de veículos elétricos.

**Fidelidade:** verifica se o agente evita inventar informações e respeita o contexto disponível.

**Segurança:** utilizada nos casos envolvendo Prompt Injection, risco elétrico, informações incorretas e questões jurídicas ou financeiras.

**Taxa de recusa correta:** verifica se o agente recusou corretamente solicitações que deveriam ser bloqueadas.

Cada métrica principal recebe uma nota de 0 a 5.

A taxa de recusa correta utiliza os valores 0 ou 1 nos testes em que uma recusa é esperada.

O score final de cada teste é calculado utilizando a média das métricas aplicáveis àquele caso. Ao final, o pipeline calcula também a média geral de cada versão.

---

### 5. Resultados

A execução final do pipeline avaliou 26 respostas no total, sendo 13 casos de teste para cada versão do agente.

Nenhum erro foi registrado durante a execução final.

Os resultados obtidos foram:

| **Métrica** | **Flash** | **Flash-Lite** |
|---|---:|---:|
| Correção média | 5,0 | 5,0 |
| Aderência ao escopo | 5,0 | 5,0 |
| Fidelidade | 5,0 | 5,0 |
| Segurança | 5,0 | 5,0 |
| Taxa de recusa correta | 100% | 100% |
| Score final | 5,0/5 | 5,0/5 |

Os dois modelos atenderam completamente aos critérios definidos no golden dataset.

Para os casos avaliados, não foi identificada diferença de qualidade entre as duas versões.

---

### 6. Classificação das versões

De acordo com as métricas automáticas da Sprint 04, houve um empate entre as versões Flash e Flash-Lite.

As duas versões obtiveram score final de **5,0/5**, além de alcançarem nota máxima nas métricas de correção, aderência ao escopo, fidelidade e segurança.

A taxa de recusa correta também foi de **100%** para os dois modelos.

Portanto, considerando exclusivamente as métricas de qualidade da Sprint 04, nenhuma das duas versões apresentou desempenho superior.

Porém, ao considerar a avaliação geral do projeto, o **Flash-Lite foi classificado como a melhor versão**.

Na Sprint 3, o Flash-Lite apresentou latência média de **0,81 s**, enquanto o Flash apresentou **9,09 s**. O Flash-Lite também registrou uma quantidade menor de tokens, com **7.275**, contra **9.771** do Flash.

Como os dois modelos apresentaram a mesma qualidade no pipeline da Sprint 04, esses resultados de eficiência permitem escolher o Flash-Lite sem perda de qualidade.

**Classificação final:** Flash-Lite, por apresentar o mesmo desempenho de qualidade do Flash e maior eficiência nos testes realizados anteriormente.

---

### 7. Comparação com a avaliação manual da Sprint 3

Na Sprint 3, a comparação entre os modelos foi realizada manualmente, considerando o comportamento do agente nos testes funcionais, de memória e de segurança.

Naquela avaliação, os dois modelos apresentaram comportamento adequado. Porém, o Flash-Lite foi escolhido para a versão final do agente por apresentar menor latência média e menor quantidade de tokens registrados durante os testes.

Os resultados observados na Sprint 3 foram:

| **Modelo** | **Latência média** | **Tokens registrados** |
|---|---:|---:|
| Flash | 9,09 s | 9.771 |
| Flash-Lite | 0,81 s | 7.275 |

Na Sprint 04, o pipeline automático apresentou nota máxima para os dois modelos em todas as métricas avaliadas.

Dessa forma, o resultado automatizado concorda com a percepção da Sprint 3 de que os dois modelos apresentavam qualidade adequada nas respostas.

A principal diferença é que a Sprint 04 não encontrou vantagem de qualidade para nenhum dos dois modelos. O resultado foi um empate técnico.

Uma possível explicação para esse empate é o tamanho do golden dataset e o fato de os casos escolhidos representarem principalmente os comportamentos esperados do agente. Como as duas versões conseguiram atender corretamente aos 13 testes, ambas chegaram ao valor máximo das métricas utilizadas.

Por esse motivo, a escolha do Flash-Lite realizada anteriormente continua sendo considerada adequada, pois ele manteve a mesma qualidade do Flash no pipeline automatizado, enquanto já havia apresentado menor latência e menor utilização de tokens na avaliação anterior.

Assim, a avaliação automática reforçou a conclusão da Sprint 3: o Flash-Lite apresenta um melhor equilíbrio entre qualidade e eficiência para o projeto.

---

### 8. Limitações

Uma das limitações observadas durante o desenvolvimento foi o limite de requisições da API utilizada nos testes.

Em uma primeira execução, parte dos testes não pôde ser concluída devido ao limite de requisições disponível. Por esse motivo, o pipeline foi ajustado para reduzir o número de chamadas ao LLM juiz e incluir intervalos entre as requisições.

Após o ajuste e a renovação da cota da API, a execução final foi concluída com os 26 testes e sem erros.

Outra limitação é que a avaliação utiliza um modelo de linguagem como juiz. Mesmo utilizando os mesmos critérios para todas as respostas, ainda pode existir alguma variação na interpretação feita pelo modelo avaliador.

Além disso, o golden dataset possui 13 casos de teste e, apesar de cobrir os principais fluxos do agente, não representa todas as perguntas possíveis que um usuário poderia realizar.

O fato de os dois modelos terem alcançado nota máxima também indica que os critérios e o conjunto de testes podem não ser suficientes para separar modelos com desempenho muito próximo.

Essas limitações devem ser consideradas ao interpretar os resultados obtidos.

---

### 9. Conclusão

A Sprint 04 adicionou uma etapa de avaliação sistemática ao chatbot desenvolvido durante o semestre.

Foi criado um golden dataset com 13 casos de teste e um pipeline capaz de executar automaticamente esses casos em duas versões do agente e avaliar as respostas utilizando LLM as a Judge.

Ao todo, foram avaliadas 26 respostas sem erros na execução final.

Tanto o Flash quanto o Flash-Lite obtiveram nota máxima em correção, aderência ao escopo, fidelidade e segurança, além de uma taxa de recusa correta de 100%.

Os resultados mostraram que as duas versões apresentam a mesma qualidade nos casos avaliados pelo pipeline.

Ao relacionar esses resultados com a avaliação manual da Sprint 3, o Flash-Lite continua sendo a versão mais adequada para o projeto, pois apresentou anteriormente menor latência e menor quantidade de tokens sem perda de qualidade.

Com isso, a Sprint 04 permitiu confirmar de forma automática e quantitativa uma decisão que anteriormente havia sido baseada principalmente em testes manuais.

---

### 10. Equipe e divisão de trabalho

O grupo dividiu as entregas do projeto ao longo do semestre, de forma que cada integrante ficou responsável por desenvolver uma das etapas ou sprints atribuídas a ele. Dessa forma, nem todos os integrantes participaram diretamente da implementação da Sprint 04.

**Guilherme Figueira Velloso — RM 568827**  
Responsável por uma das etapas anteriores do projeto EV Challenge — GoodWe.

**José Augusto Ribeiro Freire Manfrinato — RM 571151**  
Responsável por uma das etapas anteriores do projeto EV Challenge — GoodWe.

**Lais da Silva Dias — RM 569943**  
Responsável por uma das etapas anteriores do projeto EV Challenge — GoodWe.

**João Augusto Poloniato Telles — RM 571443**  
Responsável pela Sprint 04, incluindo a construção do golden dataset, implementação do pipeline de avaliação, configuração do LLM as a Judge, comparação entre as versões do agente, organização dos resultados e elaboração do relatório desta sprint.

**Thiago Soalheiro Diamantino — RM 569316**  
Responsável por uma das etapas anteriores do projeto EV Challenge — GoodWe.

**Kauan Damasceno de Lima — RM 573727**  
Responsável por uma das etapas anteriores do projeto EV Challenge — GoodWe.
