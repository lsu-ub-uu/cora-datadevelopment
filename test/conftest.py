import logging

import pytest


@pytest.fixture(autouse=True)
def no_log_files():
    """Keep tests from writing to the real logs/ directory via a configured run handler."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    root.handlers = [h for h in original_handlers if h.name != "cora-run"]
    yield
    root.handlers = original_handlers
