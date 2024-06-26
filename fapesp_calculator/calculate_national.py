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
from datetime import datetime
from pathlib import Path
from docx import Document
from python_docx_replace import docx_replace
from fapesp_calculator.por_extenso import dinheiro_por_extenso, data_por_extenso
import locale

# from dados import my_dict

HERE = Path(__file__).parent.resolve()
DATA = HERE.parent.joinpath("data").resolve()
RESULTS = HERE.joinpath("results").resolve()
import json


def generate_template_for_national_event(
    my_dict,
    event_start_date_time,
    event_end_date_time,
    current_user=None,
    extra_day=True,
    arrival_before_and_after=True,
    category="Diárias Nacionais em bolsas (exceto pós-doutorado)",
    subcategory="Com pernoite",
    template_path=HERE.joinpath("modelo_3_novo.docx"),
    filled_template_path=HERE.joinpath("modelo_preenchido.docx"),
):
    national_dict = json.loads(
        RESULTS.joinpath("fapesp_national_values.json").read_text()
    )

    national_dict_computable = {}

    for category_in_dict, category_data in national_dict.items():
        national_dict_computable[category_in_dict] = dict()

        for subcategory_in_dict, value in category_data.items():
            value = value.replace("R$ ", "")
            try:
                national_dict_computable[category_in_dict][subcategory_in_dict] = Money(
                    value.replace(",", "."), Currency.BRL
                )
            except:
                pass
    event_duration = event_end_date_time - event_start_date_time

    value_for_category = national_dict_computable[category][subcategory]

    message_to_send = f"""
    Você tem direito a {event_duration.days+1} diárias pela duração do evento
    """
    total_daily_stipends = event_duration.days + 1
    if extra_day:
        print("ok")
        print(extra_day)
        message_to_send += f"e mais uma diária por chegar antes do dia que começa e sair depois do dia que termina."
        total_daily_stipends += 1

    message_to_send += f"""
        <p> O valor que você pode solicitar para a localidade escolhida é de {value_for_category*total_daily_stipends},
        correspondendo a {total_daily_stipends} x {str(value_for_category)}. </p>
        <p> Solicite o valor no <a href="https://siaf.fapesp.br/sage/" target="_blank">SIAF</a> e justifique com o recibo abaixo.</p>

    """
    doc = Document(template_path)

    value_in_brl = value_for_category * total_daily_stipends

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

    if current_user.is_authenticated:
        print(current_user)
        print
        my_dict["n_do_processo"] = current_user.fapesp_process_number
        my_dict["nome_completo"] = current_user.full_name
        my_dict["numero_de_identidade"] = current_user.id_number
        my_dict["numero_de_CPF"] = current_user.cpf_number
        my_dict["logradouro_e_numero"] = current_user.address_number
        my_dict["complemento_de_endereco"] = current_user.address_complement
        my_dict["bairro"] = current_user.neighbourhood
        my_dict["cidade"] = current_user.city
        my_dict["estado"] = current_user.state

    my_dict["valor_unitario"] = str(value_for_category)
    my_dict["n_diarias"] = total_daily_stipends

    my_dict["cambio"] = ""

    my_dict["data_de_hoje"] = data_por_extenso(datetime.now())

    docx_replace(doc, **my_dict)

    doc.save(filled_template_path)

    return message_to_send


if __name__ == "__main__":
    my_dict = {}
    generate_template_for_national_event(
        my_dict=my_dict,
        event_start_date_time=datetime(2023, 3, 29),
        event_end_date_time=datetime(2023, 3, 31),
        category="Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos",
        subcategory="Com pernoite em: todas as capitais de estado, Brasília (DF), Araçatuba (SP), Araraquara (SP), Barretos (SP), Bauru (SP), Campinas (SP), Franca (SP), Itapeva (SP), Marília (SP), Presidente Prudente (SP), Registro (SP), Ribeirão Preto (SP), Santos (SP), São José do Rio Preto (SP), São José dos Campos (SP) e Sorocaba (SP)",
    )
