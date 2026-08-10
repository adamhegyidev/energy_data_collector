from datetime import datetime

from tools.daily.update_copernicus import (
    update_copernicus,
)
from tools.daily.update_mavir import (
    update_mavir,
)


def main():
    started_at = datetime.now()

    print(
        "=" * 60
    )

    print(
        f"Daily collection started: "
        f"{started_at.isoformat()}"
    )

    print(
        "=" * 60
    )

    print()
    print(
        "=== MAVIR ==="
    )

    mavir_ok = update_mavir()

    print()
    print(
        "=== COPERNICUS ==="
    )

    copernicus_ok = (
        update_copernicus()
    )

    finished_at = datetime.now()

    duration = (
        finished_at - started_at
    )

    print()
    print(
        "=" * 60
    )

    print(
        f"Daily collection finished: "
        f"{finished_at.isoformat()}"
    )

    print(
        f"Duration: {duration}"
    )

    print(
        f"MAVIR: "
        f"{'OK' if mavir_ok else 'ERROR'}"
    )

    print(
        f"Copernicus: "
        f"{'OK' if copernicus_ok else 'ERROR'}"
    )

    print(
        "=" * 60
    )

    if (
        not mavir_ok
        or not copernicus_ok
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()