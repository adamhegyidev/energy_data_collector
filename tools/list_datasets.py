from utils.config import get_mavir_sources


def main():
    sources = get_mavir_sources()

    print("\nAVAILABLE DATASETS\n")

    for dataset, settings in sources.items():
        enabled = settings.get("enabled", False)

        status = "ENABLED" if enabled else "DISABLED"

        print(f"{dataset:<40} {status}")


if __name__ == "__main__":
    main()