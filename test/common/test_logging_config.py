import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

from common.logging_config import HANDLER_NAME, configure_logging


@pytest.fixture(autouse=True)
def restore_root_logger():
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    root.handlers = []
    yield
    for handler in root.handlers:
        handler.close()
    root.handlers = original_handlers
    root.setLevel(original_level)


def _cora_handlers():
    return [h for h in logging.getLogger().handlers if h.name == HANDLER_NAME]


def test_returns_path_of_log_file(tmp_path):
    log_file = configure_logging("my_script", log_dir=str(tmp_path))

    assert log_file == str(tmp_path / "my_script.log")


def test_creates_log_directory(tmp_path):
    log_dir = tmp_path / "does" / "not" / "exist"

    configure_logging("my_script", log_dir=str(log_dir))

    assert log_dir.is_dir()


def test_adds_named_rotating_handler_to_root_logger(tmp_path):
    configure_logging("my_script", log_dir=str(tmp_path))

    handlers = _cora_handlers()
    assert len(handlers) == 1
    assert isinstance(handlers[0], TimedRotatingFileHandler)


def test_uses_script_name_from_argv_by_default(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["/usr/local/bin/some-entry-point", "--apply"])

    log_file = configure_logging(log_dir=str(tmp_path))

    assert log_file == str(tmp_path / "some-entry-point.log")


def test_strips_py_suffix_from_script_name(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["src/scripts/one_off/some_script.py"])

    log_file = configure_logging(log_dir=str(tmp_path))

    assert log_file == str(tmp_path / "some_script.log")


def test_second_call_does_not_add_another_handler(tmp_path):
    first = configure_logging("my_script", log_dir=str(tmp_path))
    second = configure_logging("other_script", log_dir=str(tmp_path))

    assert len(_cora_handlers()) == 1
    assert second == first


def test_sets_level_on_root_logger(tmp_path):
    configure_logging("my_script", log_dir=str(tmp_path), level=logging.DEBUG)

    assert logging.getLogger().level == logging.DEBUG


def test_silences_noisy_third_party_loggers(tmp_path):
    configure_logging("my_script", log_dir=str(tmp_path))

    for name in ("urllib3", "requests", "charset_normalizer"):
        assert logging.getLogger(name).level == logging.WARNING


def test_writes_formatted_messages_to_log_file(tmp_path):
    log_file = configure_logging("my_script", log_dir=str(tmp_path))

    logging.getLogger("some.module").info("hello")
    logging.shutdown()

    assert (
        Path(log_file).read_text(encoding="utf-8").strip().endswith(" - INFO - hello")
    )
