from collectors.mavir import download_chart
from storage.raw import save_raw_file
from database.logging import init_db, log_download

from utils.time import previous_full_day
from utils.config import get_mavir_sources


def to_millis(dt):
    return int(dt.timestamp() * 1000)


def main():

    init_db()

    from_dt, to_dt = previous_full_day()

    sources = get_mavir_sources()

    for dataset, settings in sources.items():

        if not settings["enabled"]:
            continue

        print(
            f"Collecting {dataset}"
        )

        try:

            data = download_chart(

                chart_id=settings["chart_id"],

                from_time=to_millis(
                    from_dt
                ),

                to_time=to_millis(
                    to_dt
                ),

                period=settings[
                    "export"
                ]["period"]

            )

            file_path = save_raw_file(

                source="mavir",

                dataset=dataset,

                date_value=from_dt.date(),

                content=data,

                extension=settings[
                    "export"
                ]["type"]

            )

            log_download(

                source="mavir",

                dataset=dataset,

                start_date=from_dt.date(),

                end_date=to_dt.date(),

                file_path=file_path,

                status="success",

            )

            print(
                f"Saved: {file_path}"
            )

        except Exception as error:

            log_download(

                source="mavir",

                dataset=dataset,

                start_date=from_dt.date(),

                end_date=to_dt.date(),

                status="failed",

                error_message=str(error),

            )

            print(
                f"ERROR {dataset}"
            )

            print(error)


if __name__ == "__main__":
    main()