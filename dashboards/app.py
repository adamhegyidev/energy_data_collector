from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import yaml


DATA_DIR = Path("data/processed")
LOCAL_TIMEZONE = "Europe/Budapest"


def load_sources():
    config_path = Path("config/sources.yaml")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


CONFIG = load_sources()
MAVIR_SOURCES = CONFIG.get("mavir", {})

COPERNICUS_LABELS = {
    # Nyers ERA5 mezők
    "t2m": "Levegő hőmérséklete 2 m-en - nyers (K)",
    "d2m": "Harmatpont 2 m-en - nyers (K)",
    "u10": "Szél kelet-nyugati komponense 10 m-en (m/s)",
    "v10": "Szél észak-déli komponense 10 m-en (m/s)",
    "u100": "Szél kelet-nyugati komponense 100 m-en (m/s)",
    "v100": "Szél észak-déli komponense 100 m-en (m/s)",
    "ssrd": "Felszíni beérkező napsugárzás (J/m²)",
    "tcc": "Teljes felhőborítottság - nyers (0-1)",
    "tp": "Összes csapadék - nyers (m)",
    "sp": "Felszíni légnyomás - nyers (Pa)",
    "msl": "Tengerszinti légnyomás - nyers (Pa)",

    # Származtatott mezők
    "temperature_c": "Levegő hőmérséklete 2 m-en (°C)",
    "dewpoint_c": "Harmatpont 2 m-en (°C)",

    "wind_speed_10m": "Szélsebesség 10 m-en (m/s)",
    "wind_direction_10m": "Szélirány 10 m-en (°)",

    "wind_speed_100m": "Szélsebesség 100 m-en (m/s)",
    "wind_direction_100m": "Szélirány 100 m-en (°)",

    "surface_pressure_hpa": "Felszíni légnyomás (hPa)",
    "mean_sea_level_pressure_hpa": (
        "Tengerszintre átszámított légnyomás (hPa)"
    ),
    "precipitation_mm": "Összes csapadék (mm)",
    "cloud_cover_percent": "Teljes felhőborítottság (%)",
}


def default_start_date():
    today = date.today()
    return date(today.year, today.month, 1)


def default_end_date():
    return date.today()


def add_copernicus_derived_columns(df):
    df = df.copy()

    # Hőmérsékletek: Kelvin → Celsius
    if "t2m" in df.columns:
        df["temperature_c"] = df["t2m"] - 273.15

    if "d2m" in df.columns:
        df["dewpoint_c"] = df["d2m"] - 273.15

    # Szél 10 méteren
    if {"u10", "v10"}.issubset(df.columns):
        df["wind_speed_10m"] = np.hypot(
            df["u10"],
            df["v10"],
        )

        # Meteorológiai szélirány:
        # azt mutatja, hogy honnan fúj a szél
        df["wind_direction_10m"] = (
            180
            + np.degrees(
                np.arctan2(
                    df["u10"],
                    df["v10"],
                )
            )
        ) % 360

        # Szélcsendben az irány nem értelmezhető
        df.loc[
            df["wind_speed_10m"] < 0.01,
            "wind_direction_10m",
        ] = np.nan

    # Szél 100 méteren
    if {"u100", "v100"}.issubset(df.columns):
        df["wind_speed_100m"] = np.hypot(
            df["u100"],
            df["v100"],
        )

        df["wind_direction_100m"] = (
            180
            + np.degrees(
                np.arctan2(
                    df["u100"],
                    df["v100"],
                )
            )
        ) % 360

        df.loc[
            df["wind_speed_100m"] < 0.01,
            "wind_direction_100m",
        ] = np.nan

    # Légnyomás: Pa → hPa
    if "sp" in df.columns:
        df["surface_pressure_hpa"] = df["sp"] / 100

    if "msl" in df.columns:
        df["mean_sea_level_pressure_hpa"] = df["msl"] / 100

    # Csapadék: méter → milliméter
    if "tp" in df.columns:
        df["precipitation_mm"] = df["tp"] * 1000

    # Felhőborítottság: 0-1 → százalék
    if "tcc" in df.columns:
        df["cloud_cover_percent"] = df["tcc"] * 100

    return df


def list_dirs(path):
    if not path.exists():
        return []

    return sorted(
        item.name
        for item in path.iterdir()
        if item.is_dir()
    )


def list_all_parquet_files(root):
    if not root.exists():
        return []

    return sorted(root.glob("*/*.parquet"))


def read_multiple_parquets(files):
    frames = [
        pd.read_parquet(file)
        for file in files
    ]

    if not frames:
        st.error("Nincs beolvasható parquet fájl.")
        st.stop()

    return pd.concat(
        frames,
        ignore_index=True,
    )


def filter_by_date_range(df, start_date, end_date):
    start = pd.Timestamp(start_date).tz_localize(
        LOCAL_TIMEZONE,
    )

    end = (
        pd.Timestamp(end_date)
        .tz_localize(LOCAL_TIMEZONE)
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )

    return df[
        (df["timestamp_local"] >= start)
        & (df["timestamp_local"] <= end)
    ]


def prepare_chart_df(df, value_column, aggregation):
    chart_df = df[
        [
            "timestamp_local",
            value_column,
        ]
    ].dropna()

    if aggregation == "raw":
        return chart_df

    freq_map = {
        "15 perc": "15min",
        "órás": "1h",
        "napi": "1d",
    }

    return (
        chart_df
        .set_index("timestamp_local")
        .resample(freq_map[aggregation])
        .mean()
        .reset_index()
    )


def get_mavir_display_name(dataset):
    return (
        MAVIR_SOURCES
        .get(dataset, {})
        .get("display", {})
        .get("name", dataset)
    )


def get_mavir_group(dataset):
    return (
        MAVIR_SOURCES
        .get(dataset, {})
        .get("display", {})
        .get("group", "Egyéb")
    )


def get_mavir_column_label(dataset, column):
    column_meta = (
        MAVIR_SOURCES
        .get(dataset, {})
        .get("display", {})
        .get("columns", {})
        .get(column, {})
    )

    label = column_meta.get("label", column)
    unit = column_meta.get("unit")

    if unit:
        return f"{label} ({unit})"

    return label


def build_mavir_dataset_options(datasets):
    options = {}

    for dataset in datasets:
        group = get_mavir_group(dataset)
        name = get_mavir_display_name(dataset)

        label = f"{group} / {name}"
        options[label] = dataset

    return dict(
        sorted(
            options.items(),
            key=lambda item: item[0],
        )
    )


def render_date_inputs():
    min_date = date(2000, 1, 1)
    max_date = date.today()

    start_date = st.sidebar.date_input(
        "Kezdő dátum",
        value=default_start_date(),
        min_value=min_date,
        max_value=max_date,
    )

    end_date = st.sidebar.date_input(
        "Záró dátum",
        value=default_end_date(),
        min_value=min_date,
        max_value=max_date,
    )

    if start_date > end_date:
        st.error(
            "A kezdő dátum nem lehet későbbi, "
            "mint a záró dátum."
        )
        st.stop()

    return start_date, end_date


st.set_page_config(
    page_title="Energy Data Dashboard",
    layout="wide",
)

st.title("Energy Data Dashboard")


source = st.sidebar.selectbox(
    "Adatforrás",
    [
        "mavir",
        "copernicus",
    ],
)


if source == "mavir":
    st.header("MAVIR")

    mavir_root = DATA_DIR / "mavir"
    datasets = list_dirs(mavir_root)

    if not datasets:
        st.error("Nincs feldolgozott MAVIR adat.")
        st.stop()

    dataset_options = build_mavir_dataset_options(datasets)

    selected_dataset_label = st.sidebar.selectbox(
        "Dataset",
        list(dataset_options.keys()),
    )

    dataset = dataset_options[selected_dataset_label]
    dataset_display_name = get_mavir_display_name(dataset)

    start_date, end_date = render_date_inputs()

    dataset_root = mavir_root / dataset

    files = list_all_parquet_files(dataset_root)

    if not files:
        st.error("Ehhez a datasethez nincs parquet fájl.")
        st.stop()

    df = read_multiple_parquets(files)
    df = filter_by_date_range(
        df,
        start_date,
        end_date,
    )

    if df.empty:
        st.warning("Nincs adat a kiválasztott dátumtartományban.")
        st.stop()

    period_label = f"{start_date} → {end_date}"

    st.caption(
        f"{len(files)} parquet fájl vizsgálva, "
        f"{len(df):,} sor betöltve: {period_label}"
    )

    value_columns = [
        column
        for column in df.columns
        if column not in [
            "timestamp_utc",
            "timestamp_local",
            "dataset",
        ]
    ]

    if not value_columns:
        st.error("Nincs megjeleníthető adatmező.")
        st.stop()

    selected_column = st.selectbox(
        "Megjelenítendő oszlop",
        value_columns,
        format_func=lambda column: get_mavir_column_label(
            dataset,
            column,
        ),
    )

    selected_column_label = get_mavir_column_label(
        dataset,
        selected_column,
    )

    aggregation = st.sidebar.selectbox(
        "Grafikon felbontás",
        [
            "órás",
            "15 perc",
            "napi",
            "raw",
        ],
        index=0,
    )

    chart_df = prepare_chart_df(
        df,
        selected_column,
        aggregation,
    )

    st.caption(
        f"Grafikon pontok száma: {len(chart_df):,}"
    )

    fig = px.line(
        chart_df,
        x="timestamp_local",
        y=selected_column,
        title=(
            f"MAVIR - {dataset_display_name} - "
            f"{period_label} - {selected_column_label}"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Alap statisztika")
    st.write(df[selected_column].describe())

    st.subheader("Adat előnézet")
    st.dataframe(
        df.head(200),
        use_container_width=True,
    )


if source == "copernicus":
    st.header("Copernicus ERA5")

    copernicus_dataset = "era5_hungary_points"

    copernicus_root = (
        DATA_DIR
        / "copernicus"
        / copernicus_dataset
    )

    locations = list_dirs(copernicus_root)

    if not locations:
        st.error("Nincs feldolgozott Copernicus adat.")
        st.stop()

    location = st.sidebar.selectbox(
        "Location",
        locations,
    )

    start_date, end_date = render_date_inputs()

    location_root = copernicus_root / location

    files = list_all_parquet_files(location_root)

    if not files:
        st.error("Ehhez a locationhöz nincs parquet fájl.")
        st.stop()

    df = read_multiple_parquets(files)
    df = add_copernicus_derived_columns(df)

    df = filter_by_date_range(
        df,
        start_date,
        end_date,
    )

    if df.empty:
        st.warning("Nincs adat a kiválasztott dátumtartományban.")
        st.stop()

    period_label = f"{start_date} → {end_date}"

    st.caption(
        f"{len(files)} parquet fájl vizsgálva, "
        f"{len(df):,} sor betöltve: {period_label}"
    )

    value_columns = [
        column
        for column in COPERNICUS_LABELS
        if column in df.columns
    ]

    if not value_columns:
        st.error("Nincs megjeleníthető adatmező.")
        st.stop()

    default_column = "temperature_c"

    default_index = (
        value_columns.index(default_column)
        if default_column in value_columns
        else 0
    )

    selected_column = st.selectbox(
        "Megjelenítendő oszlop",
        value_columns,
        index=default_index,
        format_func=lambda column: COPERNICUS_LABELS.get(
            column,
            column,
        ),
    )

    selected_column_label = COPERNICUS_LABELS.get(
        selected_column,
        selected_column,
    )

    aggregation = st.sidebar.selectbox(
        "Grafikon felbontás",
        [
            "órás",
            "napi",
            "raw",
        ],
        index=0,
    )

    chart_df = prepare_chart_df(
        df,
        selected_column,
        aggregation,
    )

    st.caption(
        f"Grafikon pontok száma: {len(chart_df):,}"
    )

    fig = px.line(
        chart_df,
        x="timestamp_local",
        y=selected_column,
        title=(
            f"Copernicus - {location} - "
            f"{period_label} - {selected_column_label}"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("Alap statisztika")
    st.write(df[selected_column].describe())

    st.subheader("Adat előnézet")
    st.dataframe(
        df.head(200),
        use_container_width=True,
    )