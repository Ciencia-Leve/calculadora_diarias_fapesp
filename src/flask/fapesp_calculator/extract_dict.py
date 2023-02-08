import requests
import pandas as pd
from bs4 import BeautifulSoup
from wdcuration import run_multiple_searches
import asyncio
from pathlib import Path
import json

HERE = Path(__file__).parent.resolve()
RESULTS = HERE.joinpath("results").resolve()

url = "https://fapesp.br/12042/tabela-de-diarias-de-viagem"
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
        current_strong = entry.find_all("strong")[0].text.strip()
        if (
            current_strong
            == "FAPESP: Tabela de Diárias Internacionais com pernoite - Vigente a partir de 01/10/2018"
        ):
            national_flag = 0

        if international_flag:
            country_value_dict[current_strong] = {}

        if national_flag:
            national_dict[current_strong] = {}

    if national_flag and len(entry.find_all("strong")) == 0:
        print(entry)
        print(entry.find_all("strong"))
        current_category = entry.select('td[width="83%"]')[0].text.strip()
        current_value = entry.select('td[width="14%"]')[0].text.strip()
        national_dict[current_strong][current_category] = current_value

    if international_flag:
        try:
            current_subplace = entry.select('td[valign="top"]')[0].text.strip()
            current_value = entry.select('td[valign="bottom"]')[0].text.strip()
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
