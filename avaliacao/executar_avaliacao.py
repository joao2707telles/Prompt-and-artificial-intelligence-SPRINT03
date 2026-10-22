import csv
import json
import sys
import time
from pathlib import Path

from langchain_core.messages import HumanMessage


# Permite importar os arquivos da raiz do projeto
PASTA_ATUAL = Path(__file__).resolve().parent
RAIZ_PROJETO = PASTA_ATUAL.parent

if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


from agent import criar_agente, extrair_texto
from evaluator import criar_juiz, avaliar_resposta


ARQUIVO_DATASET = PASTA_ATUAL / "golden_dataset.json"

ARQUIVO_RESULTADOS = (
    PASTA_ATUAL / "resultados_detalhados.csv"
)

ARQUIVO_RESUMO = (
    PASTA_ATUAL / "resumo_metricas.csv"
)


# Mesmos dois modelos comparados na Sprint 3
MODELOS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]


def carregar_dataset():
    with open(
        ARQUIVO_DATASET,
        "r",
        encoding="utf-8"
    ) as arquivo:
        return json.load(arquivo)


def obter_ultima_resposta(resultado):
    mensagens = resultado["messages"]

    ultima = mensagens[-1]

    return extrair_texto(ultima)


def executar_teste(
    agente,
    teste,
    nome_modelo
):
    """
    Executa um teste do golden dataset.

    Para testes de memória, mantém o mesmo thread_id
    durante todos os turnos.
    """

    thread_id = (
        f"sprint04_"
        f"{nome_modelo.replace('/', '_')}_"
        f"teste_{teste['id']}"
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Teste com vários turnos
    if "turnos" in teste:

        resultado = None

        for turno in teste["turnos"]:

            resultado = agente.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=turno
                        )
                    ]
                },
                config=config
            )

        resposta = obter_ultima_resposta(
            resultado
        )

        pergunta_avaliacao = (
            "Conversa em vários turnos:\n"
            + "\n".join(
                teste["turnos"]
            )
        )

        return (
            pergunta_avaliacao,
            resposta
        )

    # Teste normal
    pergunta = teste["pergunta"]

    resultado = agente.invoke(
        {
            "messages": [
                HumanMessage(
                    content=pergunta
                )
            ]
        },
        config=config
    )

    resposta = obter_ultima_resposta(
        resultado
    )

    return pergunta, resposta


def salvar_resultados(resultados):

    campos = [
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

        for linha in resultados:
            writer.writerow(linha)


def media_valida(
    resultados,
    modelo,
    campo
):

    valores = []

    for linha in resultados:

        if linha["modelo"] != modelo:
            continue

        valor = linha.get(campo)

        if valor is None or valor == "":
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


def taxa_recusa(
    resultados,
    modelo
):

    valores = []

    for linha in resultados:

        if linha["modelo"] != modelo:
            continue

        valor = linha.get(
            "recusa_correta"
        )

        if valor is None or valor == "":
            continue

        try:
            valores.append(int(valor))
        except (ValueError, TypeError):
            pass

    if not valores:
        return None

    return round(
        (
            sum(valores)
            / len(valores)
        ) * 100,
        2
    )


def gerar_resumo(resultados):

    resumo = []

    for modelo in MODELOS:

        linha = {
            "modelo": modelo,
            "correcao_media": media_valida(
                resultados,
                modelo,
                "correcao"
            ),
            "aderencia_escopo_media": media_valida(
                resultados,
                modelo,
                "aderencia_escopo"
            ),
            "fidelidade_media": media_valida(
                resultados,
                modelo,
                "fidelidade"
            ),
            "seguranca_media": media_valida(
                resultados,
                modelo,
                "seguranca"
            ),
            "taxa_recusa_correta_percentual": taxa_recusa(
                resultados,
                modelo
            ),
            "score_final_medio": media_valida(
                resultados,
                modelo,
                "score_final"
            )
        }

        resumo.append(linha)

    campos = [
        "modelo",
        "correcao_media",
        "aderencia_escopo_media",
        "fidelidade_media",
        "seguranca_media",
        "taxa_recusa_correta_percentual",
        "score_final_medio"
    ]

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

    juiz = criar_juiz(
        "gemini-3.5-flash"
    )

    resultados = []

    for nome_modelo in MODELOS:

        print(
            "\n----------------------------------------"
        )

        print(
            f"AVALIANDO MODELO: {nome_modelo}"
        )

        print(
            "----------------------------------------\n"
        )

        agente = criar_agente(
            model_name=nome_modelo
        )

        for teste in dataset:

            print(
                f"Teste {teste['id']} "
                f"[{teste['categoria']}]..."
            )

            try:

                pergunta, resposta = executar_teste(
                    agente,
                    teste,
                    nome_modelo
                )

                avaliacao = avaliar_resposta(
                    juiz=juiz,
                    pergunta=pergunta,
                    resposta=resposta,
                    criterio_aceite=teste[
                        "criterio_aceite"
                    ],
                    categoria=teste[
                        "categoria"
                    ]
                )

                linha = {
                    "modelo": nome_modelo,
                    "teste_id": teste["id"],
                    "categoria": teste[
                        "categoria"
                    ],
                    "pergunta": pergunta,
                    "criterio_aceite": teste[
                        "criterio_aceite"
                    ],
                    "resposta": resposta,
                    "correcao": avaliacao.get(
                        "correcao"
                    ),
                    "aderencia_escopo": avaliacao.get(
                        "aderencia_escopo"
                    ),
                    "fidelidade": avaliacao.get(
                        "fidelidade"
                    ),
                    "seguranca": avaliacao.get(
                        "seguranca"
                    ),
                    "recusa_correta": avaliacao.get(
                        "recusa_correta"
                    ),
                    "score_final": avaliacao.get(
                        "score_final"
                    ),
                    "justificativa": avaliacao.get(
                        "justificativa"
                    ),
                    "erro": ""
                }

                resultados.append(
                    linha
                )

                print(
                    f"  Score: "
                    f"{linha['score_final']}/5"
                )

            except Exception as erro:

                print(
                    f"  ERRO: {erro}"
                )

                resultados.append(
                    {
                        "modelo": nome_modelo,
                        "teste_id": teste["id"],
                        "categoria": teste[
                            "categoria"
                        ],
                        "pergunta": teste.get(
                            "pergunta",
                            "Teste multi-turno"
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

            # Salva mesmo se a execução parar depois
            salvar_resultados(
                resultados
            )

            # Pequena pausa para reduzir chance
            # de limite da API
            time.sleep(1)

    resumo = gerar_resumo(
        resultados
    )

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
            f"Modelo: {linha['modelo']}"
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
            f"SCORE FINAL: "
            f"{linha['score_final_medio']}/5"
        )

        print()

    print(
        "Arquivos gerados:"
    )

    print(
        ARQUIVO_RESULTADOS
    )

    print(
        ARQUIVO_RESUMO
    )


if __name__ == "__main__":
    main()
