import time
import certifi
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": "energy-data-collector/1.0"
})


def get(url, verify_ssl=True, retries=3, wait_seconds=60, **kwargs):
    for attempt in range(1, retries + 1):
        response = SESSION.get(
            url,
            timeout=60,
            verify=certifi.where() if verify_ssl else False,
            **kwargs
        )

        if response.status_code == 429:
            print(
                f"Too many requests. Waiting {wait_seconds} seconds "
                f"before retry {attempt}/{retries}..."
            )
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()
        return response

    raise RuntimeError(
        f"Too many requests after {retries} retries: {url}"
    )