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


levels_plus = (
    "pesquisador dirigente coordenador assessor conselheiro pós-doutorando".split()
)
levels_base = ["bolsista (menos pós-doutorado)"]

current_level = "bolsista (menos pós-doutorado)"

daily_values_national = {
    "Brasil (Pesquisadores, dirigentes, coordenadores, assessores, conselheiros e pós-doutorandos)": {
        "Com pernoite (em capitais de Estado, Angra dos Reis (RJ), Brasília (DF), Búzios (RJ) e Guarujá (SP)": Money(
            "555.00", Currency.BRL
        )
    },
    "Brasil (bolsistas menos pós-doutorandos)": {
        "Com pernoite": Money("255.00", Currency.BRL),
        "Sem pernoite": Money("170.00", Currency.BRL),
    },
}


arrival_date_time = datetime.fromisoformat("2023-03-11T00:15:00")
departure_date_time = datetime.fromisoformat("2023-03-16T00:19:00")

event_start_date_time = datetime.fromisoformat("2023-03-12T00:08:00")
event_end_date_time = datetime.fromisoformat("2023-03-16T00:16:00")

event_duration = event_end_date_time - event_start_date_time
trip_time = departure_date_time - arrival_date_time
print(event_duration.days)
print(trip_time.days)
