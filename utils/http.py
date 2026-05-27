import time
import certifi
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": "energy-data-collector/1.0"
})


def get(url, verify_ssl=True, retry_waits=None, **kwargs):
    if retry_waits is None:
        retry_waits = [15, 30, 60]

    attempts = len(retry_waits) + 1

    for attempt in range(attempts):
        try:
            response = SESSION.get(
                url,
                timeout=60,
                verify=certifi.where() if verify_ssl else False,
                **kwargs
            )

            if response.status_code == 429:
                if attempt >= len(retry_waits):
                    response.raise_for_status()

                wait_time = retry_waits[attempt]

                print(
                    f"Too many requests. Waiting {wait_time} seconds "
                    f"before retry {attempt + 1}/{len(retry_waits)}..."
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response

        except requests.exceptions.ConnectionError as error:
            if attempt >= len(retry_waits):
                raise

            wait_time = retry_waits[attempt]

            print(
                f"Connection error. Waiting {wait_time} seconds "
                f"before retry {attempt + 1}/{len(retry_waits)}..."
            )

            time.sleep(wait_time)

    raise RuntimeError(f"Request failed after retries: {url}")