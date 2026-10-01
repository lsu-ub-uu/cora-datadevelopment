import argparse
from typing import TypedDict, Any, Literal


class RequiredArgumentConfig(TypedDict):
    """Required fields for argument configuration."""

    help: str


class ArgumentConfig(RequiredArgumentConfig, total=False):
    """Configuration for a single command-line argument."""

    default: Any
    type: type
    required: bool
    action: Literal[
        "store_true",
        "store_false",
        "store",
        "store_const",
        "append",
        "append_const",
        "count",
        "version",
    ]


class ArgParserSpec(TypedDict):
    """Specification for argument parser configuration."""

    arguments: dict[str, ArgumentConfig]
    description: str


def create_argument_parser(
    description: str, arguments: dict[str, ArgumentConfig]
) -> argparse.ArgumentParser:
    """Create and configure argument parser declaratively."""
    parser = argparse.ArgumentParser(description=description)

    for name, config in arguments.items():
        config = config.copy()
        if (
            name != "--app-token"
            and "default" in config
            and config.get("action") != "store_true"
        ):
            config["help"] += f" (default: {config['default']})"
        parser.add_argument(name, **config)

    return parser


common_arguments: dict[str, ArgumentConfig] = {
    "--xml-path": {
        "help": "Path to the XML file containing source data",
        "required": False,
    },
    "--cora-url": {
        "help": "Base URL for the target Cora system",
    },
    "--system": {
        "help": "Cora system to connect to (e.g., 'preview', 'production')",
        "type": str,
    },
    "--login-id": {
        "help": "Login ID for authentication",
    },
    "--app-token": {
        "help": "Application token for authentication",
    },
    "--apply": {
        "help": "Apply changes to the Cora system (dry run if not present)",
        "action": "store_true",
    },
    "--workers": {
        "help": "Number of worker threads for processing",
        "type": int,
    },
}

cora_url_argument: dict[str, ArgumentConfig] = {
    "--cora-url": common_arguments["--cora-url"],
}

classic_arguments: dict[str, ArgumentConfig] = {
    "--fedora-url": {
        "help": "Base URL for Classic Fedora service",
    },
    "--solr-url": {
        "help": "Base URL for Classic Solr service",
    },
    "--db-host": {
        "help": "Classic database host",
    },
    "--db-port": {
        "help": "Classic database port",
        "type": int,
    },
    "--db-name": {
        "help": "Classic database name",
    },
    "--db-user": {
        "help": "Classic database user",
    },
    "--db-password": {
        "help": "Classic database password",
    },
}
