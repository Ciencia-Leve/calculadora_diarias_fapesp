from money.money import Money
from money.currency import Currency
from datetime import datetime, timedelta
from pathlib import Path
from docx import Document
from python_docx_replace import docx_replace
from flask import flash
from fapesp_calculator.por_extenso import dinheiro_por_extenso, data_por_extenso

import requests
import json

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
RESULTS = HERE.joinpath("results").resolve()


def generate_template_for_international_event(
    my_dict,
    event_start_date_time,
    event_end_date_time,
    country="Itália",
    subnational_location="Demais localidades",
    event_name_string="NOME DO EVENTO",
    event_place_string="LOCAL DO EVENTO",
    extra_day=True,
    siaf_value_brl=None,
    filled_template_path=HERE.joinpath("modelo_preenchido.docx"),
    filled_cambio_template_path=HERE.joinpath(
        "modelo_justificativa_cambio_preenchido.docx"
    ),
):

    template_path = HERE.joinpath("modelo_3_novo.docx")
    cambio_template_path = HERE.joinpath("modelo_justificativa_cambio.docx")

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

    total_value_in_usd = value_for_category * total_daily_stipends

    today = datetime.now()

    try:
        conversion_url, usd_to_brl_rate = get_conversion_for_date(today)
    except requests.exceptions.JSONDecodeError:
        flash(
            """ O cálculo dos valores em BRL não foi possível devido a um problema com a API de taxas de câmbio do Banco Central."""
        )
        message_to_send += f"""
          <p> O valor que você pode solicitar para a localidade escolhida é de {total_value_in_usd},
          correspondendo a {total_daily_stipends} x {str(value_for_category)}. </p>
      """
        return message_to_send

    brl_calculation = float(total_value_in_usd.amount) * usd_to_brl_rate

    print(brl_calculation)
    value_in_brl = Money("{:.2f}".format(round(brl_calculation, 2)), Currency.BRL)

    message_to_send += f"""
        <p> O valor que você pode solicitar para a localidade escolhida é de {total_value_in_usd},
        correspondendo a {total_daily_stipends} x {str(value_for_category)}. </p>
        <p> Considerando uma taxa de conversão de {str(usd_to_brl_rate)} (<a target="_blank" href="{conversion_url}">Plataforma Olinda - Banco Central do Brasil</a>) o valor em reais solicitado será de {value_in_brl}
        <p> Solicite o valor no <a href="https://siaf.fapesp.br/sage/" target="_blank">SIAF</a> e justifique com os recibos abaixo.</p>
    """

    if siaf_value_brl:
        siaf_value_brl = Money(siaf_value_brl.replace(",", "."), Currency.BRL)
        if siaf_value_brl < value_in_brl:
            template_path = HERE.joinpath("modelo_3_reduzido.docx")
            cambio_template_path = HERE.joinpath(
                "modelo_justificativa_cambio_reduzido.docx"
            )
            my_dict["valor_reduzido_em_reais"] = str(siaf_value_brl.amount).replace(
                ".", ","
            )
            my_dict["valor_reduzido_por_extenso"] = dinheiro_por_extenso(siaf_value_brl)
            message_to_send += f"""
                <p> Nota: O valor disponível no SIAF ({siaf_value_brl}) é menor que o valor calculado ({value_in_brl}). Usando o valor reduzido no SIAF e justificando a diferença.</p>
            """
        else:
            my_dict["valor_reduzido_em_reais"] = str(value_in_brl.amount).replace(
                ".", ","
            )
            my_dict["valor_reduzido_por_extenso"] = dinheiro_por_extenso(value_in_brl)
    else:
        my_dict["valor_reduzido_em_reais"] = str(value_in_brl.amount).replace(".", ",")
        my_dict["valor_reduzido_por_extenso"] = dinheiro_por_extenso(value_in_brl)

    doc = Document(template_path)

    my_dict["valor_em_dolar"] = str(total_value_in_usd.amount).replace(".", ",")
    my_dict["valor_em_reais"] = str(value_in_brl.amount).replace(".", ",")
    my_dict["valor_por_extenso"] = dinheiro_por_extenso(value_in_brl)
    my_dict["data_inicial"] = data_por_extenso(event_start_date_time)
    my_dict["data_final"] = data_por_extenso(event_end_date_time)

    if extra_day:
        my_dict["adendo"] = (
            " e mais 1 diária devido à chegada em dia anterior e saída em dia posterior ao evento, conforme rege o §3º da Portaria 35 da FAPESP, "
        )
    else:
        my_dict["adendo"] = ""
    my_dict["nome_do_evento"] = event_name_string
    my_dict["local_do_evento"] = event_place_string
    my_dict["data_de_hoje"] = data_por_extenso(datetime.now())
    my_dict["valor_unitario"] = str(value_for_category)
    my_dict["taxa_usd"] = str(usd_to_brl_rate)

    my_dict["n_diarias"] = total_daily_stipends

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
    print(conversion_url)
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
        siaf_value_brl="2000,00",
    )
