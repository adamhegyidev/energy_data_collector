from utils.http import get


BASE_URL = (
    "https://rtdwweb.mavir.hu/"
    "rtdwweb/webuser"
)


def download_chart(
    chart_id,
    from_time,
    to_time,
    period=15,
):

    url = (
        f"{BASE_URL}"
        f"/chart/{chart_id}/export"
    )

    params = {

        "exportType": "xlsx",

        "fromTime": from_time,

        "toTime": to_time,

        "periodType": "min",

        "period": period

    }

    # MAVIR SSL certificate rosszul van konfigurálva, ezért itt letiltjuk a SSL ellenőrzést.
    # Nem küldünk érzékeny adatokat, így ez nem jelent biztonsági kockázatot.
    # Később lehet vele baszakodni...
    response = get(
        url,
        params=params,
        verify_ssl=False
    )

    return response.content