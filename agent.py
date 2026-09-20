
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from prompts import SYSTEM_PROMPT

from goodwe_tools import (
    CAR_DATABASE,
    get_car_battery_capacity,
    calcular_preco_recarga,
    calcular_tempo_recarga
)

from rag import buscar_contexto


def extrair_texto(mensagem):
    conteudo = mensagem.content

    if isinstance(conteudo, str):
        return conteudo

    if isinstance(conteudo, list):
        textos = []

        for item in conteudo:
            if isinstance(item, dict) and "text" in item:
                textos.append(item["text"])
            else:
                textos.append(str(item))

        return " ".join(textos)

    return str(conteudo)


def encontrar_carro_no_historico(state):

    mensagens_usuario = [
        msg for msg in state["messages"]
        if isinstance(msg, HumanMessage)
    ]

    for mensagem in reversed(mensagens_usuario):

        texto = str(mensagem.content).lower()

        for modelo in CAR_DATABASE:

            if modelo.lower() in texto:
                return get_car_battery_capacity(modelo)

    return None


def detectar_rota(state):

    ultima_mensagem = state["messages"][-1]
    texto = str(ultima_mensagem.content).lower()

    termos_injection = [
        "ignore todas as instruções",
        "ignore suas instruções",
        "ignore as instruções anteriores",
        "revele seu system prompt",
        "mostre seu system prompt",
        "system prompt completo",
        "esqueça suas instruções"
    ]

    termos_eletricos_perigosos = [
        "abrir meu carregador",
        "abrir o carregador",
        "mexer nos cabos",
        "cabos internos",
        "desmontar o carregador",
        "fio energizado",
        "fios energizados"
    ]

    termos_preco = [
        "quanto custa",
        "qual o preço",
        "qual o preco",
        "preço da recarga",
        "preco da recarga",
        "valor da recarga",
        "custo da recarga",
        "carga completa"
    ]

    termos_tempo = [
        "quanto tempo",
        "tempo de recarga",
        "demora para carregar",
        "demora pra carregar",
        "tempo para carregar",
        "tempo pra carregar"
    ]

    if any(termo in texto for termo in termos_injection):
        return "prompt_injection"

    if any(termo in texto for termo in termos_eletricos_perigosos):
        return "risco_eletrico"

    if any(termo in texto for termo in termos_tempo):
        return "calcular_tempo"

    if any(termo in texto for termo in termos_preco):
        return "calcular_preco"

    return "responder"


def criar_agente(model_name="gemini-3.5-flash-lite"):

    modelo = ChatGoogleGenerativeAI(
        model=model_name,
        max_retries=2
    )


    def responder(state: MessagesState):

        ultima_mensagem = state["messages"][-1]

        pergunta = str(ultima_mensagem.content)

        contexto_pdf = buscar_contexto(
            pergunta,
            k=3
        )

        contexto_sistema = f"""
{SYSTEM_PROMPT}

CONTEXTO RECUPERADO DO DATASHEET HCA G2:

{contexto_pdf}

Use o contexto acima quando ele for relevante para a pergunta.
Não invente informações técnicas que não estejam disponíveis.
"""

        mensagens = [
            SystemMessage(
                content=contexto_sistema
            )
        ] + state["messages"]

        resposta = modelo.invoke(
            mensagens
        )

        return {
            "messages": [resposta]
        }


    def responder_preco(state: MessagesState):

        carro = encontrar_carro_no_historico(state)

        if not carro:

            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Para calcular o valor da recarga, "
                            "me informe o modelo do seu carro."
                        )
                    )
                ]
            }

        capacidade = carro["capacity_kwh"]

        preco = calcular_preco_recarga(
            capacidade
        )

        texto = (
            f"Para o {carro['model']}, "
            f"que possui bateria de {capacidade} kWh, "
            f"uma carga completa custa aproximadamente "
            f"R$ {preco:.2f}."
        )

        return {
            "messages": [
                AIMessage(content=texto)
            ]
        }


    def responder_tempo(state: MessagesState):

        carro = encontrar_carro_no_historico(state)

        if not carro:

            return {
                "messages": [
                    AIMessage(
                        content=(
                            "Para estimar o tempo de recarga, "
                            "me informe o modelo do seu carro."
                        )
                    )
                ]
            }

        capacidade = carro["capacity_kwh"]

        tempo = calcular_tempo_recarga(
            capacidade,
            22
        )

        texto = (
            f"Considerando um carregador de 22 kW, "
            f"uma carga completa do {carro['model']} "
            f"levaria aproximadamente "
            f"{tempo['horas']} hora(s) e "
            f"{tempo['minutos']} minuto(s)."
        )

        return {
            "messages": [
                AIMessage(content=texto)
            ]
        }


    def bloquear_prompt_injection(state: MessagesState):

        return {
            "messages": [
                AIMessage(
                    content=(
                        "Não posso ignorar minhas instruções internas "
                        "nem revelar configurações ou prompts privados. "
                        "Posso continuar ajudando com carregadores "
                        "GoodWe e mobilidade elétrica."
                    )
                )
            ]
        }


    def bloquear_risco_eletrico(state: MessagesState):

        return {
            "messages": [
                AIMessage(
                    content=(
                        "Por segurança, não posso fornecer um passo a passo "
                        "para abrir equipamentos ou manipular componentes "
                        "elétricos energizados. "
                        "Procure um profissional habilitado."
                    )
                )
            ]
        }


    memoria = InMemorySaver()

    builder = StateGraph(MessagesState)

    builder.add_node("responder", responder)
    builder.add_node("calcular_preco", responder_preco)
    builder.add_node("calcular_tempo", responder_tempo)

    builder.add_node(
        "bloquear_prompt_injection",
        bloquear_prompt_injection
    )

    builder.add_node(
        "bloquear_risco_eletrico",
        bloquear_risco_eletrico
    )

    builder.add_conditional_edges(
        START,
        detectar_rota,
        {
            "responder": "responder",
            "calcular_preco": "calcular_preco",
            "calcular_tempo": "calcular_tempo",
            "prompt_injection": "bloquear_prompt_injection",
            "risco_eletrico": "bloquear_risco_eletrico"
        }
    )

    builder.add_edge("responder", END)
    builder.add_edge("calcular_preco", END)
    builder.add_edge("calcular_tempo", END)
    builder.add_edge("bloquear_prompt_injection", END)
    builder.add_edge("bloquear_risco_eletrico", END)

    return builder.compile(
        checkpointer=memoria
    )
