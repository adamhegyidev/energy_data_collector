from pathlib import Path

import yaml


CATEGORY_NAMES = {
    "aktualis_ver": "Aktuális VER",
    "ver_netto_forgalmi": "VER nettó forgalmi adatok",
    "energia_mix": "Energia mix",
    "teljes_brutto_felhasznalas": "Teljes bruttó villamosenergia-felhasználás",
    "szabalyozasi_adatok": "Szabályozási adatok",
}


DATASET_NAMES = {
    "eromuvi_termeles": "Erőművi termelés",
    "frekvencia": "Hálózati frekvencia",
    "hatarmetszeki_aramlasok": "Határmetszéki áramlások",
    "import_export": "Import / export",
    "rendszer_adatok": "Rendszeradatok",
    "terv_es_teny_rendszerterhelesek": "Terv és tény rendszerterhelések",

    "frekvencia_adatok": "Frekvencia adatok",
    "napi_csucskihasznaltsagi_oraszam": "Napi csúcskihasználtsági óraszám",
    "napi_szabadkereskedelmi_villamosenergia_igeny": "Napi szabadkereskedelmi villamosenergia-igény",
    "ver_tenyleges_netto_forgalmi_napi_komulalt_adatok": "VER tényleges nettó forgalmi napi kumulált adatok",
    "ver_tenyleges_netto_forgalmi_negyedoras_adatok": "VER tényleges nettó forgalmi negyedórás adatok",

    "co2_kibocsatas": "CO₂ kibocsátás",
    "co2_kibocsatas_aranya_a_brutto_hazai_eromuvi_termelesben": "CO₂ kibocsátás aránya a bruttó hazai erőművi termelésben",
    "co2_kibocsatas_aranya_a_brutto_rendszerterhelesben": "CO₂ kibocsátás aránya a bruttó rendszerterhelésben",

    "hmke_pv_termeles": "HMKE PV termelés",
    "ipari_pv_termeles": "Ipari PV termelés",
    "ipari_szel_termeles": "Ipari széltermelés",
    "megujulo_hazai_brutto_termeles_terv_teny": "Megújuló hazai bruttó termelés terv/tény",
    "megujulo_termelesi_aranyok_a_brutto_hazai_eromuvi_termelesben": "Megújuló termelési arányok a bruttó hazai erőművi termelésben",
    "megujulo_termelesi_aranyok_a_brutto_rendszerterhelesben": "Megújuló termelési arányok a bruttó rendszerterhelésben",
    "pv_szumma_halozatra_kiadott": "PV szumma hálózatra kiadott",
    "pv_szumma_tenylegesen_megtermelt": "PV szumma ténylegesen megtermelt",
    "sajat_celu_scte_ipari_pv_termeles": "Saját célú SCTE ipari PV termelés",

    "brutto_energia_havi": "Bruttó energia havi",
    "brutto_energia_napi": "Bruttó energia napi",
    "brutto_energia_eves": "Bruttó energia éves",

    "aktivalas_kiegyenlito_szabalyozas_celjabol_igcc": "Aktiválás kiegyenlítő szabályozás céljából IGCC",
    "aktivalas_kiegyenlito_es_nem_kiegyenlito_szabalyozas_celjabol_igcc": "Aktiválás kiegyenlítő és nem kiegyenlítő szabályozás céljából IGCC",
    "aktivalas_nem_kiegyenlito_szabalyozas_celjabol": "Aktiválás nem kiegyenlítő szabályozás céljából",
    "aktivalas_nem_kiegyenlito_szabalyozas_celjabol_reszletes_anonim": "Aktiválás nem kiegyenlítő szabályozás céljából, részletes anonim",
}


def prettify_name(dataset_key):
    return dataset_key.replace("_", " ").capitalize()


def main():
    config_path = Path("config/sources.yaml")

    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    mavir_sources = config.get("mavir", {})

    for dataset_key, settings in mavir_sources.items():
        category = settings.get("category")

        display = settings.get("display", {})

        display["name"] = DATASET_NAMES.get(
            dataset_key,
            prettify_name(dataset_key),
        )

        display["group"] = CATEGORY_NAMES.get(
            category,
            category,
        )

        display.setdefault(
            "description",
            display["name"],
        )

        display.setdefault(
            "columns",
            {},
        )

        settings["display"] = display

    with config_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            config,
            file,
            allow_unicode=True,
            sort_keys=False,
        )

    print(f"Updated: {config_path}")


if __name__ == "__main__":
    main()
