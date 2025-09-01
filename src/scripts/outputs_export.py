import argparse
from fedora_to_cora.export_publications_from_fedora import (
    export_publications_from_fedora,
)


def main():
    parser = argparse.ArgumentParser(
        description="Export publications from Fedora for a domain"
    )

    parser.add_argument(
        "--domain",
        required=True,
        help="Domain to export publications from (e.g., 'varldskulturmuserna')",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Number of worker threads to use (default: 16)",
    )

    args = parser.parse_args()

    export_publications_from_fedora(args.domain, workers=args.workers)


if __name__ == "__main__":
    main()
