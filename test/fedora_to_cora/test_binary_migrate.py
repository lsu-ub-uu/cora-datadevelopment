from unittest.mock import patch
from xml.etree import ElementTree as ET

import pytest

from cora.context import MockContext
from fedora_to_cora.binary_migrate import migrate_binary


def test_missing_fedora_url_fails_before_download(monkeypatch):
    monkeypatch.delenv("FEDORA_URL", raising=False)
    with patch("fedora_to_cora.binary_migrate.requests.get") as request:
        with pytest.raises(ValueError, match="FEDORA_URL"):
            migrate_binary(
                ET.Element("record"), "pid", "file", MockContext(), fedora_url=None
            )
    request.assert_not_called()
