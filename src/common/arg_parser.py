import argparse
import os
from typing import TypedDict, Any, Literal
from dotenv import load_dotenv

load_dotenv()


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
        "required": False,
    },
    "--system": {
        "help": "Cora system to connect to (e.g., 'preview', 'production')",
        "type": str,
        "default": os.environ.get("CORA_SYSTEM", "minikube"),
    },
    "--login-id": {
        "default": os.environ.get("CORA_LOGIN_ID", "divaAdmin@cora.epc.ub.uu.se"),
        "help": "Login ID for authentication",
    },
    "--app-token": {
        "default": os.environ.get("CORA_APP_TOKEN"),
        "help": "Application token for authentication",
    },
    "--apply": {
        "help": "Apply changes to the Cora system (dry run if not present)",
        "action": "store_true",
    },
    "--workers": {
        "help": "Number of worker threads for processing",
        "type": int,
        "default": int(os.environ.get("CORA_WORKERS", "16")),
    },
}

classic_arguments: dict[str, ArgumentConfig] = {
    "--fedora-url": {
        "help": "Base URL for Classic Fedora service",
        "default": os.environ.get("FEDORA_URL"),
    },
    "--solr-url": {
        "help": "Base URL for Classic Solr service",
        "default": os.environ.get("SOLR_URL"),
    },
    "--db-host": {
        "help": "Classic database host",
        "default": os.environ.get("DB_HOST", "localhost"),
    },
    "--db-port": {
        "help": "Classic database port",
        "type": int,
        "default": int(os.environ.get("DB_PORT", "5432")),
    },
    "--db-name": {
        "help": "Classic database name",
        "default": os.environ.get("DB_NAME", "auradb"),
    },
    "--db-user": {
        "help": "Classic database user",
        "default": os.environ.get("DB_USER"),
    },
    "--db-password": {
        "help": "Classic database password",
        "default": os.environ.get("DB_PASSWORD"),
    },
}
