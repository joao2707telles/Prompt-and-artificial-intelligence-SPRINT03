
import difflib


CAR_DATABASE = {
    "BYD Dolphin Mini": 38.8,
    "BYD Dolphin": 44.9,
    "BYD Dolphin GS": 60.4,
    "BYD Yuan Plus": 60.5,
    "BYD Seal": 82.5,
    "BYD Han": 85.4,
    "BYD Tan": 108.8,
    "BYD Song Plus": 18.3,
    "BYD Song Pro": 18.3,
    "BYD King": 18.3,
    "GWM Ora 03 Skin": 48.0,
    "GWM Ora 03 GT": 63.0,
    "GWM Haval H6 PHEV19": 19.0,
    "GWM Haval H6 PHEV35": 34.0,
    "GWM Haval H6 GT": 34.0,
    "Volvo EX30": 69.0,
    "Volvo XC40": 82.0,
    "Volvo C40": 82.0,
    "Volvo EX90": 111.0,
    "Volvo XC60 T8": 18.8,
    "Volvo XC90 T8": 18.8,
    "Porsche Taycan": 105.0,
    "Porsche Macan Electric": 100.0,
    "BMW iX1": 64.7,
    "BMW iX": 111.5,
    "Renault Kwid E-Tech": 26.8,
    "Renault Megane E-Tech": 60.0,
    "Caoa Chery iCar": 30.1,
    "Audi Q8 e-tron": 114.0,
    "Mercedes-Benz EQS": 107.8,
    "Mercedes Benz EQS": 107.8,
    "Mercedes EQS": 107.8,
    "Fiat 500e": 42.0
}


LOCAIS_CARREGADORES = [
    "MorumbiShopping",
    "Shopping Interlagos",
    "Shopping SP Market",
    "Shopping Vila Olímpia",
    "Shopping Cidade Jardim",
    "Shopping Ibirapuera",
    "JK Iguatemi",
    "Shopping Iguatemi São Paulo"
]


CARREGADORES_HCA = {
    "HCA GW 22K": {
        "preco": 7775.00,
        "potencia_kw": 22
    },

    "HCA GW 11K": {
        "preco": 4680.44,
        "potencia_kw": 11
    },

    "HCA GW 7K": {
        "preco": 4188.00,
        "potencia_kw": 7
    }
}


def get_car_battery_capacity(car_model):
    """
    Procura o modelo do veículo no banco da Sprint 2.
    """

    for model, capacity in CAR_DATABASE.items():

        if car_model.lower() in model.lower():

            return {
                "model": model,
                "capacity_kwh": capacity
            }

    modelos_originais = list(CAR_DATABASE.keys())

    modelos_minusculos = {
        modelo.lower(): modelo
        for modelo in modelos_originais
    }

    matches = difflib.get_close_matches(
        car_model.lower(),
        modelos_minusculos.keys(),
        n=1,
        cutoff=0.5
    )

    if matches:

        modelo_correto = modelos_minusculos[
            matches[0]
        ]

        return {
            "model": modelo_correto,
            "capacity_kwh": CAR_DATABASE[
                modelo_correto
            ]
        }

    return {
        "error": (
            "Modelo não encontrado "
            "na base de veículos."
        )
    }


def calcular_preco_recarga(capacidade_kwh):
    """
    Fórmula utilizada na Sprint 2:
    bateria × R$ 0,50.
    """

    return round(
        capacidade_kwh * 0.50,
        2
    )


def calcular_tempo_recarga(
    capacidade_kwh,
    potencia_kw=22
):
    """
    Estimativa simplificada de carga completa.
    """

    horas = capacidade_kwh / potencia_kw

    horas_inteiras = int(horas)

    minutos = round(
        (horas - horas_inteiras) * 60
    )

    return {
        "horas_decimal": round(horas, 2),
        "horas": horas_inteiras,
        "minutos": minutos
    }
