import csv
import json
import sys
import time
from pathlib import Path

from langchain_core.messages import HumanMessage


# Pastas do projeto
PASTA_AVALIACAO = Path(__file__).resolve().parent
RAIZ_PROJETO = PASTA_AVALIACAO.parent

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from agent import criar_agente, extrair_texto
from evaluator import criar_juiz, avaliar_lote


ARQUIVO_DATASET = PASTA_AVALIACAO / "golden_dataset.json"
ARQUIVO_RESULTADOS = PASTA_AVALIACAO / "resultados_detalhados.csv"
ARQUIVO_RESUMO = PASTA_AVALIACAO / "resumo_metricas.csv"


# Mantemos as mesmas versões usadas na Sprint 3.
VERSOES = [
    {
        "nome": "Flash",
        "modelo": "gemini-3.5-flash"
    },
    {
        "nome": "Flash-Lite",
        "modelo": "gemini-3.5-flash-lite"
    }
]


def carregar_dataset():
    with open(
        ARQUIVO_DATASET,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def pegar_resposta(resultado):
    mensagem = resultado["messages"][-1]
    return extrair_texto(mensagem)


def executar_teste(agente, teste, versao):
    """
    Executa um caso do golden dataset.
    """

    thread_id = (
        f"sprint04_{versao}_teste_{teste['id']}"
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Caso com memória e vários turnos
    if "turnos" in teste:
        resultado = None

        for turno in teste["turnos"]:
            resultado = agente.invoke(
                {
                    "messages": [
                        HumanMessage(content=turno)
                    ]
                },
                config=config
            )

            # Evita excesso de chamadas por minuto
            time.sleep(13)

        resposta = pegar_resposta(resultado)

        pergunta = (
            "Conversa em vários turnos:\n"
            + "\n".join(teste["turnos"])
        )

        return pergunta, resposta

    # Caso normal
    pergunta = teste["pergunta"]

    resultado = agente.invoke(
        {
            "messages": [
                HumanMessage(content=pergunta)
            ]
        },
        config=config
    )

    resposta = pegar_resposta(resultado)

    return pergunta, resposta


def executar_com_retry(
    agente,
    teste,
    versao,
    tentativas=3
):
    """
    Faz novas tentativas em erros temporários da API.
    """

    for tentativa in range(1, tentativas + 1):
        try:
            return executar_teste(
                agente,
                teste,
                versao
            )

        except Exception as erro:
            texto_erro = str(erro)

            temporario = (
                "429" in texto_erro
                or "503" in texto_erro
                or "RESOURCE_EXHAUSTED" in texto_erro
                or "UNAVAILABLE" in texto_erro
            )

            if not temporario:
                raise

            if tentativa == tentativas:
                raise

            print(
                f"  Erro temporário. "
                f"Tentativa {tentativa}/{tentativas}."
            )

            time.sleep(30)


def salvar_resultados(resultados):
    campos = [
        "versao",
        "modelo",
        "teste_id",
        "categoria",
        "pergunta",
        "criterio_aceite",
        "resposta",
        "correcao",
        "aderencia_escopo",
        "fidelidade",
        "seguranca",
        "recusa_correta",
        "score_final",
        "justificativa",
        "erro"
    ]

    with open(
        ARQUIVO_RESULTADOS,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos
        )

        writer.writeheader()
        writer.writerows(resultados)


def media(resultados, versao, campo):
    valores = []

    for linha in resultados:
        if linha["versao"] != versao:
            continue

        valor = linha.get(campo)

        if valor in [None, ""]:
            continue

        try:
            valores.append(float(valor))
        except (ValueError, TypeError):
            pass

    if not valores:
        return None

    return round(
        sum(valores) / len(valores),
        2
    )


def taxa_recusa(resultados, versao):
    valores = []

    for linha in resultados:
        if linha["versao"] != versao:
            continue

        valor = linha.get("recusa_correta")

        if valor in [None, ""]:
            continue

        valores.append(int(valor))

    if not valores:
        return None

    return round(
        (sum(valores) / len(valores)) * 100,
        2
    )


def gerar_resumo(resultados):
    resumo = []

    for versao in VERSOES:
        nome = versao["nome"]

        linha = {
            "versao": nome,
            "modelo": versao["modelo"],
            "correcao_media": media(
                resultados,
                nome,
                "correcao"
            ),
            "aderencia_escopo_media": media(
                resultados,
                nome,
                "aderencia_escopo"
            ),
            "fidelidade_media": media(
                resultados,
                nome,
                "fidelidade"
            ),
            "seguranca_media": media(
                resultados,
                nome,
                "seguranca"
            ),
            "taxa_recusa_correta_percentual": taxa_recusa(
                resultados,
                nome
            ),
            "score_final_medio": media(
                resultados,
                nome,
                "score_final"
            )
        }

        resumo.append(linha)

    campos = list(resumo[0].keys())

    with open(
        ARQUIVO_RESUMO,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        writer = csv.DictWriter(
            arquivo,
            fieldnames=campos
        )

        writer.writeheader()
        writer.writerows(resumo)

    return resumo


def main():
    print(
        "\n=== SPRINT 04 - PIPELINE DE AVALIAÇÃO ===\n"
    )

    dataset = carregar_dataset()

    print(
        f"Golden dataset carregado: "
        f"{len(dataset)} testes\n"
    )

    resultados = []

    # Juiz separado das duas versões avaliadas
    juiz = criar_juiz(
        model_name="gemini-3.8-flash"
    )

    for versao in VERSOES:

        nome = versao["nome"]
        modelo = versao["modelo"]

        print(
            "\n----------------------------------------"
        )
        print(
            f"AVALIANDO VERSÃO: {nome}"
        )
        print(
            f"MODELO: {modelo}"
        )
        print(
            "----------------------------------------\n"
        )

        agente = criar_agente(
            model_name=modelo
        )

        testes_para_juiz = []

        # Primeiro o agente responde
        for teste in dataset:

            print(
                f"Teste {teste['id']} "
                f"[{teste['categoria']}]..."
            )

            try:
                pergunta, resposta = executar_com_retry(
                    agente,
                    teste,
                    nome
                )

                linha = {
                    "versao": nome,
                    "modelo": modelo,
                    "teste_id": teste["id"],
                    "categoria": teste["categoria"],
                    "pergunta": pergunta,
                    "criterio_aceite": teste[
                        "criterio_aceite"
                    ],
                    "resposta": resposta,
                    "correcao": "",
                    "aderencia_escopo": "",
                    "fidelidade": "",
                    "seguranca": "",
                    "recusa_correta": "",
                    "score_final": "",
                    "justificativa": "",
                    "erro": ""
                }

                resultados.append(linha)

                testes_para_juiz.append(
                    {
                        "teste_id": teste["id"],
                        "categoria": teste["categoria"],
                        "pergunta": pergunta,
                        "criterio_aceite": teste[
                            "criterio_aceite"
                        ],
                        "resposta": resposta
                    }
                )

                print("  Resposta obtida.")

            except Exception as erro:
                print(
                    f"  ERRO: {erro}"
                )

                resultados.append(
                    {
                        "versao": nome,
                        "modelo": modelo,
                        "teste_id": teste["id"],
                        "categoria": teste["categoria"],
                        "pergunta": teste.get(
                            "pergunta",
                            "Teste de memória"
                        ),
                        "criterio_aceite": teste[
                            "criterio_aceite"
                        ],
                        "resposta": "",
                        "correcao": "",
                        "aderencia_escopo": "",
                        "fidelidade": "",
                        "seguranca": "",
                        "recusa_correta": "",
                        "score_final": "",
                        "justificativa": "",
                        "erro": str(erro)
                    }
                )

            # Salva as respostas mesmo antes do juiz
            salvar_resultados(resultados)

            time.sleep(13)

        print(
            f"\nEnviando respostas da versão "
            f"{nome} para o LLM Judge..."
        )

        # Uma única chamada do juiz para a versão inteira
        if testes_para_juiz:
            try:
                avaliacoes = avaliar_lote(
                    juiz,
                    testes_para_juiz
                )

                avaliacoes_por_id = {
                    int(item["teste_id"]): item
                    for item in avaliacoes
                }

                for linha in resultados:
                    if linha["versao"] != nome:
                        continue

                    avaliacao = avaliacoes_por_id.get(
                        int(linha["teste_id"])
                    )

                    if not avaliacao:
                        continue

                    linha["correcao"] = avaliacao.get(
                        "correcao",
                        ""
                    )

                    linha[
                        "aderencia_escopo"
                    ] = avaliacao.get(
                        "aderencia_escopo",
                        ""
                    )

                    linha["fidelidade"] = avaliacao.get(
                        "fidelidade",
                        ""
                    )

                    linha["seguranca"] = avaliacao.get(
                        "seguranca",
                        ""
                    )

                    linha[
                        "recusa_correta"
                    ] = avaliacao.get(
                        "recusa_correta",
                        ""
                    )

                    linha["score_final"] = avaliacao.get(
                        "score_final",
                        ""
                    )

                    linha["justificativa"] = avaliacao.get(
                        "justificativa",
                        ""
                    )

                salvar_resultados(resultados)

                print(
                    "Avaliação automática concluída."
                )

            except Exception as erro:
                print(
                    f"Erro no LLM Judge: {erro}"
                )

    resumo = gerar_resumo(resultados)

    print(
        "\n========================================"
    )
    print(
        "RESULTADOS FINAIS"
    )
    print(
        "========================================\n"
    )

    for linha in resumo:

        print(
            f"Versão: {linha['versao']}"
        )

        print(
            f"Correção: "
            f"{linha['correcao_media']}"
        )

        print(
            f"Aderência ao escopo: "
            f"{linha['aderencia_escopo_media']}"
        )

        print(
            f"Fidelidade: "
            f"{linha['fidelidade_media']}"
        )

        print(
            f"Segurança: "
            f"{linha['seguranca_media']}"
        )

        print(
            f"Recusa correta: "
            f"{linha['taxa_recusa_correta_percentual']}%"
        )

        print(
            f"Score final: "
            f"{linha['score_final_medio']}/5"
        )

        print()

    print(
        "Arquivos gerados:"
    )

    print(ARQUIVO_RESULTADOS)
    print(ARQUIVO_RESUMO)


if __name__ == "__main__":
    main()
