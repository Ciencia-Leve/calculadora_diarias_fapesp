import requests
import pandas as pd
from bs4 import BeautifulSoup
from wdcuration import run_multiple_searches
import asyncio
from pathlib import Path
import json

HERE = Path(__file__).parent.resolve()
RESULTS = HERE.joinpath("results").resolve()

url = "https://fapesp.br/16590/tabela-de-diarias-de-viagem"
html = requests.get(url).text
soup = BeautifulSoup(html, "lxml")

# HTML locator identified with help of https://webscraper.io/
entries = soup.find_all("tr")

international_flag = 0
national_flag = 0
country_value_dict = {}
national_dict = {}
for entry in entries:
    if entry.text.strip() == "":
        continue
    if len(entry.find_all("strong")) > 0:
        current_strong = entry.select("td")[0].text.strip()

        if (
            current_strong
            == "FAPESP: Tabela de Diárias Nacionais - Vigente a partir de 01/03/2024"
        ):
            national_flag = 1

        if international_flag:
            country_value_dict[current_strong] = {}

        if national_flag:
            national_dict[current_strong] = {}

    if national_flag != 0 and international_flag == 0:
        print(entry)
        print(entry.find_all("strong"))
        current_category = entry.select("td")[0].text.strip()
        try:
            current_value = entry.select("td")[1].text.strip()
        except IndexError:
            continue

        if current_strong not in national_dict:
            national_dict[current_strong] = {}

        national_dict[current_strong][current_category] = current_value

    if international_flag:
        try:
            current_subplace = entry.select("td")[1].text.strip()
            current_strong = entry.select("td")[0].text.strip()
            current_value = entry.select("td")[2].text.strip()
            if current_strong not in country_value_dict:
                country_value_dict[current_strong] = {}

            country_value_dict[current_strong][current_subplace] = current_value
        except:
            continue
    if current_strong == "País":
        international_flag = 1
        national_flag = 0
    if current_strong == "Diárias Nacionais em Auxílios":
        national_flag = 1

RESULTS.joinpath("fapesp_international_values.json").write_text(
    json.dumps(country_value_dict, indent=4, sort_keys=True, ensure_ascii=False)
)


RESULTS.joinpath("fapesp_national_values.json").write_text(
    json.dumps(national_dict, indent=4, sort_keys=True, ensure_ascii=False)
)
