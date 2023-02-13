from fapesp_calculator.calculate_international import *
from fapesp_calculator.calculate_national import *

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
