from money.money import Money
from money.currency import Currency
from datetime import datetime
import math


contador_vinte = "zero um dois três quatro cinco seis sete oito nove dez onze doze treze catorze quinze dezesseis dezessete dezoito dezenove vinte".split()
contador_dezenas = (
    "zero dez vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
)

contador_centenas = "zero cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()

contador_meses = "skip janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()


def data_por_extenso(data):
    data_por_extenso = f"{str(data.day)} de {contador_meses[data.month]} de {data.year}"
    return data_por_extenso


def dinheiro_por_extenso(valor):
    currency_dict = {"BRL": "reais", "USD": "dólares estadounidenses"}

    frac, whole = math.modf(valor.amount)

    extenso = ate_milhares_por_extenso(whole)
    extenso += " " + currency_dict[valor.currency.name]
    frac = round(frac, 2)
    if frac != 0:
        frac = frac * 100
        extenso += " e " + dezenas_por_extenso(frac) + " centavos"
    return extenso


def dezenas_por_extenso(n):
    n = int(n)
    if n <= 20:
        return contador_vinte[n]
    else:
        unidades = n % 10
        dezenas = int((n % 100 - n % 10) / 10)

        if unidades == 0:
            return contador_dezenas[dezenas]
        return contador_dezenas[dezenas] + " e " + contador_vinte[unidades]


def centenas_por_extenso(n):
    if n < 100:
        return dezenas_por_extenso(n)
    if n == 100:
        return "cem"
    else:
        dezenas_e_unidades = int(n % 100)
        centenas = int((n % 1000 - dezenas_e_unidades) / 100)
        return (
            contador_centenas[centenas]
            + " e "
            + dezenas_por_extenso(dezenas_e_unidades)
        )


def ate_milhares_por_extenso(n):
    n = int(n)

    if n < 1000:
        return centenas_por_extenso(n)
    if n == 1000:
        return "mil"

    milhares = int(n / 1000)
    centenas = n % 1000
    dezenas = n % 100

    if milhares == 1:
        if centenas > 100 and dezenas != 0:
            return "mil " + centenas_por_extenso(centenas)
        else:
            return "mil e " + centenas_por_extenso(centenas)
    if centenas > 100 and dezenas != 0:
        return centenas_por_extenso(milhares) + " mil " + centenas_por_extenso(centenas)

    return centenas_por_extenso(milhares) + " mil e " + centenas_por_extenso(centenas)


def main():
    n = 1020
    print(ate_milhares_por_extenso(n))


if __name__ == "__main__":
    main()
