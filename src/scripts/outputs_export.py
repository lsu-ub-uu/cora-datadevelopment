from common.arg_parser import create_argument_parser, classic_arguments
from fedora_to_cora.export_publications_from_fedora import (
    export_publications_from_fedora,
)


def main():
    parser = create_argument_parser(
        description="Export publications from Fedora for a specified domain and save to disk",
        arguments={
            "--domain": {
                "required": True,
                "help": "Domain to export publications from (e.g., 'varldskulturmuserna')",
            },
            "--workers": {
                "type": int,
                "default": 16,
                "help": "Number of worker threads to use (default: 16)",
            },
            **classic_arguments,
        },
    )

    args = parser.parse_args()

    export_publications_from_fedora(
        args.domain,
        workers=args.workers,
        solr_url=args.solr_url,
        fedora_url=args.fedora_url,
    )


if __name__ == "__main__":
    main()
