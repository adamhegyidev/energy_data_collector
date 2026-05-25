from pathlib import Path


def save_raw_file(source, dataset, date_value, content, extension="xlsx"):
    path = Path(
        "data"
    ) / "raw" / source / dataset / str(date_value.year) / f"{date_value.month:02d}"

    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{date_value}.{extension}"

    with open(file_path, "wb") as file:
        file.write(content)

    return file_path