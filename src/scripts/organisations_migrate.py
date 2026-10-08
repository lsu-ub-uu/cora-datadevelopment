from common.arg_parser import create_argument_parser, common_arguments
from common.environment import load_environment
from common.logging_config import configure_logging
from cora.context import CoraContext
from cora_to_cora.organisations_migrate import organisations_migrate


def main():
    load_environment()
    parser = create_argument_parser(
        description="Import organistations from Classic Cora",
        arguments={
            **common_arguments,
            "--domain": {
                "help": "Domain to migrate organisations for (omit to migrate all domains)",
                "type": str,
                "required": False,
            },
        },
    )

    args = parser.parse_args()

    configure_logging()
    context = CoraContext(
        system=args.system,
        login_id=args.login_id,
        app_token=args.app_token,
        workers=args.workers,
        cora_url=args.cora_url,
    )
    organisations_migrate(context, args.domain)


if __name__ == "__main__":
    main()
