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
