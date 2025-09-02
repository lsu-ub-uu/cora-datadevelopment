"""Tests for arg_parser module."""

import pytest
import argparse
from common.arg_parser import create_argument_parser, ArgumentConfig


def test_create_argument_parser_basic():
    """Test basic argument parser creation."""
    arguments: dict[str, ArgumentConfig] = {
        "--verbose": {
            "action": "store_true",
            "help": "Enable verbose output",
        }
    }

    parser = create_argument_parser("Test parser", arguments)
    assert isinstance(parser, argparse.ArgumentParser)


def test_create_argument_parser_with_required_argument():
    """Test argument parser with required argument."""
    arguments: dict[str, ArgumentConfig] = {
        "--input-file": {
            "required": True,
            "help": "Input file path",
            "type": str,
        },
        "--output-file": {
            "required": False,
            "help": "Output file path",
            "type": str,
            "default": "output.txt",
        },
    }

    parser = create_argument_parser("Test parser with required args", arguments)

    # Test that required argument is enforced
    with pytest.raises(SystemExit):
        parser.parse_args([])

    # Test that providing required argument works
    args = parser.parse_args(["--input-file", "test.txt"])
    assert args.input_file == "test.txt"
    assert args.output_file == "output.txt"


def test_create_argument_parser_optional_vs_required():
    """Test mix of optional and required arguments."""
    arguments: dict[str, ArgumentConfig] = {
        "--required-arg": {
            "required": True,
            "help": "This argument is required",
            "type": str,
        },
        "--optional-arg": {
            "required": False,
            "help": "This argument is optional",
            "type": str,
            "default": "default_value",
        },
        "--flag": {
            "action": "store_true",
            "help": "Boolean flag",
        },
    }

    parser = create_argument_parser("Mixed required/optional test", arguments)

    # Should fail without required argument
    with pytest.raises(SystemExit):
        parser.parse_args(["--flag"])

    # Should work with required argument
    args = parser.parse_args(["--required-arg", "value"])
    assert args.required_arg == "value"
    assert args.optional_arg == "default_value"
    assert args.flag is False

    # Should work with all arguments
    args = parser.parse_args(
        ["--required-arg", "value", "--optional-arg", "custom", "--flag"]
    )
    assert args.required_arg == "value"
    assert args.optional_arg == "custom"
    assert args.flag is True


def test_argument_config_typing():
    """Test that ArgumentConfig typing works correctly."""
    # This should be valid
    config: ArgumentConfig = {
        "help": "Test help",
        "required": True,
        "type": str,
    }

    # This should also be valid (required is optional)
    config2: ArgumentConfig = {
        "help": "Test help",
        "type": str,
        "default": "default_val",
    }

    assert config["required"] is True
    assert "required" not in config2
