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
        if "default" in config and config.get("action") != "store_true":
            config["help"] += f" (default: {config['default']})"
        parser.add_argument(name, **config)

    return parser


common_arguments: dict[str, ArgumentConfig] = {
    "--xml-path": {
        "help": "Path to the XML file containing source data",
        "required": True,
    },
    "--system": {
        "help": "Cora system to connect to (e.g., 'preview', 'production')",
        "type": str,
        "default": "preview",
    },
    "--login-id": {
        "default": "divaAdmin@cora.epc.ub.uu.se",
        "help": "Login ID for authentication",
    },
    "--app-token": {
        "default": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
        "help": "Application token for authentication",
    },
    "--apply": {
        "help": "Apply changes to the Cora system (dry run if not present)",
        "action": "store_true",
    },
    "--workers": {
        "help": "Number of worker threads for processing",
        "type": int,
        "default": 16,
    },
}
