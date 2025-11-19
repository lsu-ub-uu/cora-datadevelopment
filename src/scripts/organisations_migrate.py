from common.arg_parser import create_argument_parser, common_arguments
from cora.context import CoraContext
from cora_to_cora.organisations_migrate import organisations_migrate


def main():
    parser = create_argument_parser(
        description="Import organistations from Classic Cora",
        arguments={
            "--system": {
                "help": "Cora system to connect to (e.g., 'preview', 'production')",
                "type": str,
                "default": "preview",
            },
            "--domain": {
                "help": "Domain to migrate organisations for",
                "type": str,
                "required": True,
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "default": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
                "help": "Application token for authentication",
            },
            "--workers": {
                "help": "Number of worker threads for processing",
                "type": int,
                "default": 16,
            },
        },
    )

    args = parser.parse_args()

    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
    )
    organisations_migrate(context, args.domain)


if __name__ == "__main__":
    main()
