import argparse
from fedora_to_cora.process_fedora_publication_files import (
    process_fedora_publication_files,
)

# Default environment configuration
DEFAULT_ENV = {
    "xml_dir": "data/fedora_xml/varldskulturmuseerna/20250625",
    "system": "pre",
    "login_id": "divaAdmin@cora.epc.ub.uu.se",
    "app_token": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
    "apply": False,
}


def main():
    """Main entry point for the outputs import script."""
    parser = argparse.ArgumentParser(
        description="Process Fedora XML publication files and import them to Cora"
    )

    parser.add_argument(
        "--xml-dir",
        default=DEFAULT_ENV["xml_dir"],
        help=f"Directory containing XML files to process (default: {DEFAULT_ENV['xml_dir']})",
    )

    parser.add_argument(
        "--system",
        default=DEFAULT_ENV["system"],
        help=f"Target system for migration (default: {DEFAULT_ENV['system']})",
    )

    parser.add_argument(
        "--login-id",
        default=DEFAULT_ENV["login_id"],
        help=f"Login ID for authentication (default: {DEFAULT_ENV['login_id']})",
    )

    parser.add_argument(
        "--app-token",
        default=DEFAULT_ENV["app_token"],
        help="Application token for authentication (default: uses preset token)",
    )
cc
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform actual transformations (default is false)",
    )

    args = parser.parse_args()

    env = {
        "xml_dir": args.xml_dir,
        "system": args.system,
        "login_id": args.login_id,
        "app_token": args.app_token,
        "apply": args.apply,
    }

    process_fedora_publication_files(**env)


if __name__ == "__main__":
    main()
