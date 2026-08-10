from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml


DATA_DIR = Path("data/processed")
LOCAL_TIMEZONE = "Europe/Budapest"


# ==========================================================
# CONFIG
# ==========================================================

def load_sources():
    config_path = Path("config/sources.yaml")

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


CONFIG = load_sources()
MAVIR_SOURCES = CONFIG.get("mavir", {})


# ==========================================================
# COPERNICUS META
# ==========================================================

COPERNICUS_FIELDS = {
    # Származtatott mezők
    "temperature_c": {
        "label": "Levegő hőmérséklete 2 m-en",
        "unit": "°C",
    },
    "dewpoint_c": {
        "label": "Harmatpont 2 m-en",
        "unit": "°C",
    },
    "wind_speed_10m": {
        "label": "Szélsebesség 10 m-en",
        "unit": "m/s",
    },
    "wind_direction_10m": {
        "label": "Szélirány 10 m-en",
        "unit": "°",
    },
    "wind_speed_100m": {
        "label": "Szélsebesség 100 m-en",
        "unit": "m/s",
    },
    "wind_direction_100m": {
        "label": "Szélirány 100 m-en",
        "unit": "°",
    },
    "surface_pressure_hpa": {
        "label": "Felszíni légnyomás",
        "unit": "hPa",
    },
    "mean_sea_level_pressure_hpa": {
        "label": "Tengerszintre átszámított légnyomás",
        "unit": "hPa",
    },
    "precipitation_mm": {
        "label": "Összes csapadék",
        "unit": "mm",
    },
    "cloud_cover_percent": {
        "label": "Teljes felhőborítottság",
        "unit": "%",
    },

    # Nyers ERA5 mezők
    "t2m": {
        "label": "Levegő hőmérséklete 2 m-en – nyers",
        "unit": "K",
    },
    "d2m": {
        "label": "Harmatpont 2 m-en – nyers",
        "unit": "K",
    },
    "u10": {
        "label": "Szél kelet–nyugati komponense 10 m-en",
        "unit": "m/s",
    },
    "v10": {
        "label": "Szél észak–déli komponense 10 m-en",
        "unit": "m/s",
    },
    "u100": {
        "label": "Szél kelet–nyugati komponense 100 m-en",
        "unit": "m/s",
    },
    "v100": {
        "label": "Szél észak–déli komponense 100 m-en",
        "unit": "m/s",
    },
    "ssrd": {
        "label": "Felszíni beérkező napsugárzás",
        "unit": "J/m²",
    },
    "tcc": {
        "label": "Teljes felhőborítottság – nyers",
        "unit": "0–1",
    },
    "tp": {
        "label": "Összes csapadék – nyers",
        "unit": "m",
    },
    "sp": {
        "label": "Felszíni légnyomás – nyers",
        "unit": "Pa",
    },
    "msl": {
        "label": "Tengerszinti légnyomás – nyers",
        "unit": "Pa",
    },
}


# ==========================================================
# DATE
# ==========================================================

def default_start_date():
    today = date.today()

    return date(
        today.year,
        today.month,
        1,
    )


def default_end_date():
    return date.today()


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


# ==========================================================
# FILE HELPERS
# ==========================================================

def list_dirs(path):
    if not path.exists():
        return []

    return sorted(
        item.name
        for item in path.iterdir()
        if item.is_dir()
    )


def iter_year_months(
    start_date,
    end_date,
):
    year = start_date.year
    month = start_date.month

    while (
        year,
        month,
    ) <= (
        end_date.year,
        end_date.month,
    ):
        yield year, month

        month += 1

        if month == 13:
            month = 1
            year += 1


def get_parquet_files_for_range(
    root,
    start_date,
    end_date,
):
    files = []

    for year, month in iter_year_months(
        start_date,
        end_date,
    ):
        file_path = (
            root
            / str(year)
            / f"{year}-{month:02d}.parquet"
        )

        if file_path.exists():
            files.append(file_path)

    return files


@st.cache_data(show_spinner=False)
def read_parquet_files(file_paths):
    frames = []

    for file_path in file_paths:
        frames.append(
            pd.read_parquet(file_path)
        )

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )


def filter_date_range(
    df,
    start_date,
    end_date,
):
    if df.empty:
        return df

    start = (
        pd.Timestamp(start_date)
        .tz_localize(
            LOCAL_TIMEZONE
        )
    )

    end = (
        pd.Timestamp(end_date)
        .tz_localize(
            LOCAL_TIMEZONE
        )
        + pd.Timedelta(days=1)
    )

    return df[
        (
            df["timestamp_local"]
            >= start
        )
        & (
            df["timestamp_local"]
            < end
        )
    ].copy()


# ==========================================================
# COPERNICUS DERIVED
# ==========================================================

def add_copernicus_derived_columns(df):
    df = df.copy()

    if "t2m" in df.columns:
        df["temperature_c"] = (
            df["t2m"] - 273.15
        )

    if "d2m" in df.columns:
        df["dewpoint_c"] = (
            df["d2m"] - 273.15
        )

    if {"u10", "v10"}.issubset(df.columns):
        df["wind_speed_10m"] = np.hypot(
            df["u10"],
            df["v10"],
        )

        df["wind_direction_10m"] = (
            180
            + np.degrees(
                np.arctan2(
                    df["u10"],
                    df["v10"],
                )
            )
        ) % 360

        df.loc[
            df["wind_speed_10m"] < 0.01,
            "wind_direction_10m",
        ] = np.nan

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

    if "sp" in df.columns:
        df["surface_pressure_hpa"] = (
            df["sp"] / 100
        )

    if "msl" in df.columns:
        df["mean_sea_level_pressure_hpa"] = (
            df["msl"] / 100
        )

    if "tp" in df.columns:
        df["precipitation_mm"] = (
            df["tp"] * 1000
        )

    if "tcc" in df.columns:
        df["cloud_cover_percent"] = (
            df["tcc"] * 100
        )

    return df


# ==========================================================
# MAVIR META
# ==========================================================

def get_mavir_display_name(dataset):
    return (
        MAVIR_SOURCES
        .get(dataset, {})
        .get("display", {})
        .get(
            "name",
            dataset,
        )
    )


def get_mavir_group(dataset):
    return (
        MAVIR_SOURCES
        .get(dataset, {})
        .get("display", {})
        .get(
            "group",
            "Egyéb",
        )
    )


def get_mavir_column_meta(
    dataset,
    column,
):
    settings = MAVIR_SOURCES.get(
        dataset,
        {},
    )

    display = settings.get(
        "display",
        {},
    )

    column_meta = (
        display
        .get("columns", {})
        .get(column, {})
    )

    label = column_meta.get(
        "label",
        column,
    )

    unit = column_meta.get(
        "unit",
        display.get("unit", ""),
    )

    return label, unit


# ==========================================================
# SAMPLE COLUMNS
# ==========================================================

@st.cache_data(show_spinner=False)
def get_mavir_dataset_columns(dataset):
    root = (
        DATA_DIR
        / "mavir"
        / dataset
    )

    files = sorted(
        root.glob("*/*.parquet")
    )

    if not files:
        return []

    df = pd.read_parquet(
        files[0]
    )

    return [
        column
        for column in df.columns
        if column not in [
            "timestamp_utc",
            "timestamp_local",
            "dataset",
        ]
    ]


@st.cache_data(show_spinner=False)
def get_copernicus_available_fields(location):
    root = (
        DATA_DIR
        / "copernicus"
        / "era5_hungary_points"
        / location
    )

    files = sorted(
        root.glob("*/*.parquet")
    )

    if not files:
        return []

    df = pd.read_parquet(
        files[0]
    )

    df = add_copernicus_derived_columns(
        df
    )

    return [
        field
        for field in COPERNICUS_FIELDS
        if field in df.columns
    ]


# ==========================================================
# SERIES STATE
# ==========================================================

if "selected_series" not in st.session_state:
    st.session_state.selected_series = []


def series_id(meta):
    if meta["source"] == "mavir":
        return (
            "mavir:"
            f"{meta['dataset']}:"
            f"{meta['column']}"
        )

    return (
        "copernicus:"
        f"{meta['location']}:"
        f"{meta['column']}"
    )


def add_series(meta):
    new_id = series_id(meta)

    existing_ids = {
        series_id(item)
        for item in st.session_state.selected_series
    }

    if new_id not in existing_ids:
        st.session_state.selected_series.append(
            meta
        )


def remove_series(index):
    st.session_state.selected_series.pop(
        index
    )


# ==========================================================
# SERIES LOAD
# ==========================================================

def load_mavir_series(
    meta,
    start_date,
    end_date,
):
    root = (
        DATA_DIR
        / "mavir"
        / meta["dataset"]
    )

    files = get_parquet_files_for_range(
        root,
        start_date,
        end_date,
    )

    if not files:
        return pd.DataFrame()

    df = read_parquet_files(
        tuple(
            str(file)
            for file in files
        )
    )

    df = filter_date_range(
        df,
        start_date,
        end_date,
    )

    column = meta["column"]

    if column not in df.columns:
        return pd.DataFrame()

    return (
        df[
            [
                "timestamp_utc",
                "timestamp_local",
                column,
            ]
        ]
        .rename(
            columns={
                column: "value",
            }
        )
    )


def load_copernicus_series(
    meta,
    start_date,
    end_date,
):
    root = (
        DATA_DIR
        / "copernicus"
        / "era5_hungary_points"
        / meta["location"]
    )

    files = get_parquet_files_for_range(
        root,
        start_date,
        end_date,
    )

    if not files:
        return pd.DataFrame()

    df = read_parquet_files(
        tuple(
            str(file)
            for file in files
        )
    )

    df = filter_date_range(
        df,
        start_date,
        end_date,
    )

    df = add_copernicus_derived_columns(
        df
    )

    column = meta["column"]

    if column not in df.columns:
        return pd.DataFrame()

    return (
        df[
            [
                "timestamp_utc",
                "timestamp_local",
                column,
            ]
        ]
        .rename(
            columns={
                column: "value",
            }
        )
    )


# ==========================================================
# AGGREGATION
# ==========================================================

def aggregate_series(
    df,
    aggregation,
):
    if df.empty:
        return df

    if aggregation == "raw":
        return df

    freq_map = {
        "15 perc": "15min",
        "órás": "1h",
        "napi": "1d",
    }

    return (
        df
        .set_index(
            "timestamp_utc"
        )[["value"]]
        .resample(
            freq_map[aggregation]
        )
        .mean()
        .reset_index()
    )


# ==========================================================
# CHART
# ==========================================================

def create_comparison_chart(
    loaded_series,
):
    fig = go.Figure()

    units = []

    for item in loaded_series:
        unit_key = item["unit_key"]

        if unit_key not in units:
            units.append(
                unit_key
            )

    axis_map = {
        unit_key: index + 1
        for index, unit_key
        in enumerate(units)
    }

    for item in loaded_series:
        axis_number = axis_map[
            item["unit_key"]
        ]

        axis_ref = (
            "y"
            if axis_number == 1
            else f"y{axis_number}"
        )

        df = item["df"]

        x_column = (
            "timestamp_utc"
            if "timestamp_utc"
            in df.columns
            else df.columns[0]
        )

        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df["value"],
                mode="lines",
                name=item["label"],
                yaxis=axis_ref,
                connectgaps=False,
            )
        )

    layout_updates = {}

    for index, unit_key in enumerate(
        units
    ):
        axis_number = index + 1

        layout_name = (
            "yaxis"
            if axis_number == 1
            else f"yaxis{axis_number}"
        )

        display_unit = next(
            item["unit"]
            for item in loaded_series
            if item["unit_key"]
            == unit_key
        )

        axis_config = {
            "title": display_unit,
            "showgrid": (
                axis_number == 1
            ),
        }

        if axis_number > 1:
            axis_config[
                "overlaying"
            ] = "y"

            axis_config[
                "side"
            ] = (
                "right"
                if axis_number % 2 == 0
                else "left"
            )

            axis_config[
                "anchor"
            ] = "free"

            if (
                axis_config["side"]
                == "right"
            ):
                axis_config[
                    "position"
                ] = min(
                    1.0,
                    0.98
                    - (
                        (axis_number - 2)
                        // 2
                    )
                    * 0.045,
                )

            else:
                axis_config[
                    "position"
                ] = max(
                    0.0,
                    0.02
                    + (
                        (axis_number - 3)
                        // 2
                    )
                    * 0.045,
                )

        layout_updates[
            layout_name
        ] = axis_config

    fig.update_layout(
        **layout_updates
    )

    fig.update_layout(
        height=850,
        hovermode="x unified",

        xaxis={
            "title": "Idő",
            "domain": [
                0.08,
                0.92,
            ],
        },

        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.15,
            "xanchor": "left",
            "x": 0,
        },

        margin={
            "t": 80,
            "b": 220,
            "l": 100,
            "r": 100,
        },
    )
    
    return fig


# ==========================================================
# STREAMLIT PAGE
# ==========================================================

st.set_page_config(
    page_title="Energy Data Dashboard",
    layout="wide",
)

st.title(
    "Energy Data Dashboard"
)

st.caption(
    "MAVIR és Copernicus idősorok "
    "közös összehasonlítása."
)


# ==========================================================
# GLOBAL CONTROLS
# ==========================================================

start_date, end_date = (
    render_date_inputs()
)

aggregation = (
    st.sidebar.selectbox(
        "Grafikon felbontás",
        [
            "órás",
            "15 perc",
            "napi",
            "raw",
        ],
        index=0,
    )
)


# ==========================================================
# ADD SERIES
# ==========================================================

st.subheader(
    "Adatsor hozzáadása"
)

source_type = st.radio(
    "Forrás",
    [
        "MAVIR",
        "Copernicus",
    ],
    horizontal=True,
)


# ==========================================================
# MAVIR SELECTOR
# ==========================================================

if source_type == "MAVIR":
    mavir_root = (
        DATA_DIR
        / "mavir"
    )

    datasets = list_dirs(
        mavir_root
    )

    groups = sorted(
        {
            get_mavir_group(dataset)
            for dataset in datasets
        }
    )

    selected_group = st.selectbox(
        "Csoport",
        groups,
    )

    group_datasets = [
        dataset
        for dataset in datasets
        if get_mavir_group(dataset)
        == selected_group
    ]

    dataset_options = {
        get_mavir_display_name(
            dataset
        ): dataset
        for dataset
        in group_datasets
    }

    selected_dataset_name = (
        st.selectbox(
            "Dataset",
            sorted(
                dataset_options.keys()
            ),
        )
    )

    selected_dataset = (
        dataset_options[
            selected_dataset_name
        ]
    )

    columns = (
        get_mavir_dataset_columns(
            selected_dataset
        )
    )

    column_labels = {}

    for column in columns:
        label, unit = (
            get_mavir_column_meta(
                selected_dataset,
                column,
            )
        )

        display = label

        if unit:
            display += (
                f" ({unit})"
            )

        column_labels[
            display
        ] = column

    selected_column_labels = (
        st.multiselect(
            "Mezők",
            options=list(
                column_labels.keys()
            ),
        )
    )

    if st.button(
        "Kiválasztott MAVIR adatsorok hozzáadása",
        type="primary",
    ):
        for selected_label in (
            selected_column_labels
        ):
            column = column_labels[
                selected_label
            ]

            label, unit = (
                get_mavir_column_meta(
                    selected_dataset,
                    column,
                )
            )

            # Ha nincs unit metadata,
            # ne rakjuk automatikusan más
            # ismeretlen egységű mezővel közös tengelyre.
            unit_key = (
                unit
                if unit
                else (
                    f"unknown:"
                    f"{selected_dataset}:"
                    f"{column}"
                )
            )

            add_series(
                {
                    "source": "mavir",
                    "dataset":
                        selected_dataset,
                    "column": column,
                    "label": (
                        f"{selected_dataset_name}"
                        f" – {label}"
                    ),
                    "unit": (
                        unit
                        if unit
                        else "ismeretlen"
                    ),
                    "unit_key":
                        unit_key,
                }
            )


# ==========================================================
# COPERNICUS SELECTOR
# ==========================================================

if source_type == "Copernicus":
    copernicus_root = (
        DATA_DIR
        / "copernicus"
        / "era5_hungary_points"
    )

    locations = list_dirs(
        copernicus_root
    )

    selected_locations = (
        st.multiselect(
            "Helyszínek",
            locations,
        )
    )

    if selected_locations:
        common_fields = None

        for location in (
            selected_locations
        ):
            fields = set(
                get_copernicus_available_fields(
                    location
                )
            )

            if common_fields is None:
                common_fields = fields
            else:
                common_fields &= fields

        common_fields = sorted(
            common_fields or []
        )

        field_options = {
            (
                f"{COPERNICUS_FIELDS[field]['label']}"
                f" ({COPERNICUS_FIELDS[field]['unit']})"
            ): field
            for field in common_fields
        }

        selected_field_labels = (
            st.multiselect(
                "Mezők",
                list(
                    field_options.keys()
                ),
            )
        )

        if st.button(
            "Kiválasztott Copernicus adatsorok hozzáadása",
            type="primary",
        ):
            for location in (
                selected_locations
            ):
                for field_label in (
                    selected_field_labels
                ):
                    field = (
                        field_options[
                            field_label
                        ]
                    )

                    meta = (
                        COPERNICUS_FIELDS[
                            field
                        ]
                    )

                    add_series(
                        {
                            "source":
                                "copernicus",
                            "location":
                                location,
                            "column":
                                field,
                            "label": (
                                f"{location}"
                                f" – "
                                f"{meta['label']}"
                            ),
                            "unit":
                                meta["unit"],
                            "unit_key":
                                meta["unit"],
                        }
                    )


# ==========================================================
# SELECTED SERIES
# ==========================================================

st.divider()

st.subheader(
    "Kiválasztott adatsorok"
)

if not st.session_state.selected_series:
    st.info(
        "Még nincs kiválasztott adatsor."
    )

else:
    for index, item in enumerate(
        st.session_state.selected_series
    ):
        col1, col2, col3 = st.columns(
            [
                6,
                2,
                1,
            ]
        )

        col1.write(
            item["label"]
        )

        col2.write(
            item["unit"]
        )

        if col3.button(
            "Törlés",
            key=f"delete_{index}",
        ):
            remove_series(index)
            st.rerun()

    if st.button(
        "Összes törlése"
    ):
        st.session_state.selected_series = []
        st.rerun()


# ==========================================================
# LOAD DATA
# ==========================================================

if not st.session_state.selected_series:
    st.stop()


loaded_series = []

with st.spinner(
    "Adatok betöltése..."
):
    for meta in (
        st.session_state.selected_series
    ):
        if meta["source"] == "mavir":
            df = load_mavir_series(
                meta,
                start_date,
                end_date,
            )

        else:
            df = load_copernicus_series(
                meta,
                start_date,
                end_date,
            )

        if df.empty:
            st.warning(
                f"Nincs adat: "
                f"{meta['label']}"
            )
            continue

        df = aggregate_series(
            df,
            aggregation,
        )

        loaded_series.append(
            {
                **meta,
                "df": df,
            }
        )


if not loaded_series:
    st.warning(
        "A kiválasztott időszakban "
        "nincs megjeleníthető adat."
    )
    st.stop()


# ==========================================================
# SUMMARY
# ==========================================================

st.divider()

col1, col2, col3, col4 = (
    st.columns(4)
)

units = {
    item["unit_key"]
    for item in loaded_series
}

col1.metric(
    "Adatsorok",
    len(loaded_series),
)

col2.metric(
    "Y tengelyek",
    len(units),
)

col3.metric(
    "Kezdő dátum",
    str(start_date),
)

col4.metric(
    "Záró dátum",
    str(end_date),
)


# ==========================================================
# GRAPH
# ==========================================================

st.subheader(
    "Összehasonlítás"
)

st.caption(
    "Az azonos mértékegységű adatsorok "
    "automatikusan ugyanarra az Y tengelyre kerülnek."
)

fig = create_comparison_chart(
    loaded_series
)

fig.update_layout(
    title=(
        f"{start_date} → {end_date}"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ==========================================================
# TABLE
# ==========================================================

st.subheader(
    "Adatsorok összesítése"
)

summary_rows = []

for item in loaded_series:
    series = item["df"]["value"]

    summary_rows.append(
        {
            "Adatsor":
                item["label"],
            "Mértékegység":
                item["unit"],
            "Pontok":
                len(series),
            "Hiányzó":
                int(
                    series.isna().sum()
                ),
            "Minimum":
                series.min(),
            "Átlag":
                series.mean(),
            "Medián":
                series.median(),
            "Maximum":
                series.max(),
            "Szórás":
                series.std(),
        }
    )


summary_df = pd.DataFrame(
    summary_rows
)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)