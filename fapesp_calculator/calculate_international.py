# https://fapesp.br/12042/tabela-de-diarias-de-viagem

# Portaria 35:
# IV - Diária com pernoite: valor concedido por dia, destinado a custear as despesas com alimentação,
# hospedagem e locomoção urbana, quando há deslocamento do município sede com a realização de pousada;
# V - Diária sem pernoite: valor concedido por dia, destinado a custear as despesas com alimentação e
# locomoção urbana, quando há deslocamento do município sede sem a realização de pousada;
# VI - Diária para refeições: valor concedido por dia, destinado a custear as despesas com alimentação,
# para participação em evento no mesmo município sede, mas fora da Instituição Sede;

# X - Município sede:
# a) para os outorgados: município em que se localiza a Instituição Sede do projeto, indicada no processo; e
# b) para membros de equipe não vinculados à Instituição que sedia o projeto: município em que se localiza a Instituição de vínculo do respectivo membro de equipe;


# § 3º Nos casos em que, devido aos horários da programação oficial de um ou mais eventos,
# for necessário chegar no dia anterior ao seu início e retornar no dia seguinte ao seu término,
#  poderá ser considerada uma diária adicional aos dias dos eventos, respeitados os limites definidos nos Arts. 5º e 6º.

# § 4º Para fins de manutenção mensal, na contagem da fração de mês, será sempre considerado mês comercial de trinta dias.

# § 5º A adequação dos gastos com diárias e manutenção mensal será analisada pela FAPESP com base nas justificativas
# e documentos comprobatórios enviados nos Relatórios Científicos e Prestações de Contas,
# a serem apresentados conforme normas específicas,
#  nas datas estabelecidas no Termo de Outorga e Aceitação de Auxílios e Bolsas.

# § 6º O pagamento de diárias e manutenção mensal no país para pesquisadores que não sejam
# membros de equipe aprovados pela FAPESP poderá ser realizado nas seguintes hipóteses:

from money.money import Money
from money.currency import Currency
from datetime import datetime, timedelta
from pathlib import Path
from docx import Document
from python_docx_replace import docx_replace
from por_extenso import dinheiro_por_extenso, data_por_extenso
import requests

# from dados import my_dict

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
RESULTS = HERE.joinpath("results").resolve()
import json


def generate_template_for_international_event(
    my_dict,
    event_start_date_time,
    event_end_date_time,
    country="Itália",
    subnational_location="Demais localidades",
    event_name_string="NOME DO EVENTO",
    event_place_string="LOCAL DO EVENTO",
    extra_day=True,
    template_path=HERE.joinpath("modelo_3_novo.docx"),
    cambio_template_path=HERE.joinpath("modelo_justificativa_cambio.docx"),
    filled_template_path=HERE.joinpath("modelo_preenchido.docx"),
    filled_cambio_template_path=HERE.joinpath(
        "modelo_justificativa_cambio_preenchido.docx"
    ),
):
    international_values_dict = json.loads(
        RESULTS.joinpath("fapesp_international_values.json").read_text(encoding="UTF-8")
    )

    international_values_dict_computable = {}

    for country_for_dict, country_data in international_values_dict.items():
        international_values_dict_computable[country_for_dict] = dict()

        for location_for_dict, value in country_data.items():
            international_values_dict_computable[country_for_dict][
                location_for_dict
            ] = Money(value.replace(",", "."), Currency.USD)

    event_duration = event_end_date_time - event_start_date_time

    value_for_category = international_values_dict_computable[country][
        subnational_location
    ]

    message_to_send = f"""
    Você tem direito a {event_duration.days+1} diárias pela duração do evento
    """
    total_daily_stipends = event_duration.days + 1
    if extra_day:
        message_to_send += f"e mais uma diária por chegar antes do dia que começa e sair depois do dia que termina."
        total_daily_stipends += 1

    value_in_usd = value_for_category * total_daily_stipends

    today = datetime.now()

    conversion_url, usd_to_brl_rate = get_conversion_for_date(today)

    brl_calculation = float(value_in_usd.amount) * usd_to_brl_rate

    print(brl_calculation)
    value_in_brl = Money("{:.2f}".format(round(brl_calculation, 2)), Currency.BRL)

    message_to_send += f"""
        <p> O valor que você pode solicitar para a localidade escolhida é de {value_in_usd},
        correspondendo a {total_daily_stipends} x {str(value_for_category)}. </p>
        <p> Considerando uma taxa de conversão de {str(usd_to_brl_rate)} (<a target="_blank" href="{conversion_url}">Plataforma Olinda - Banco Central do Brasil</a>) o valor em reais solicitado será de {value_in_brl}
    """
    doc = Document(template_path)

    my_dict["valor_em_dolar"] = str(value_in_usd.amount).replace(".", ",")
    my_dict["valor_em_reais"] = str(value_in_brl.amount).replace(".", ",")
    my_dict["valor_por_extenso"] = dinheiro_por_extenso(value_in_brl)
    my_dict["data_inicial"] = data_por_extenso(event_start_date_time)
    my_dict["data_final"] = data_por_extenso(event_end_date_time)
    my_dict["taxa_usd"] = str(usd_to_brl_rate)

    if extra_day:
        my_dict[
            "adendo"
        ] = " e mais 1 diária devido à chegada em dia anterior e saída em dia posterior ao evento, conforme rege o §3º da Portaria 35 da FAPESP, "
    else:
        my_dict["adendo"] = ""
    my_dict["nome_do_evento"] = event_name_string
    my_dict["local_do_evento"] = event_place_string
    my_dict["data_de_hoje"] = data_por_extenso(datetime.now())

    docx_replace(doc, **my_dict)

    doc.save(filled_template_path)

    cambio_doc = Document(cambio_template_path)

    my_dict["chamada_de_api"] = conversion_url
    docx_replace(cambio_doc, **my_dict)

    cambio_doc.save(filled_cambio_template_path)
    return message_to_send


def get_conversion_for_date(today):
    day_for_url = today.strftime("%m-%d-%Y")

    conversion_url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{day_for_url}'&$top=100&$format=json&$select=cotacaoCompra,dataHoraCotacao"

    r = requests.get(conversion_url)
    data = r.json()
    if len(data["value"]) == 0:
        day = today - timedelta(1)
        conversion_url, usd_to_brl_rate = get_conversion_for_date(day)

    else:
        usd_to_brl_rate = float(data["value"][0]["cotacaoCompra"])
    return conversion_url, usd_to_brl_rate


if __name__ == "__main__":
    generate_template_for_international_event(
        my_dict={},
        country="Alemanha",
        subnational_location="Hamburgo",
        event_start_date_time=datetime(2023, 3, 29),
        event_end_date_time=datetime(2023, 3, 31),
    )
