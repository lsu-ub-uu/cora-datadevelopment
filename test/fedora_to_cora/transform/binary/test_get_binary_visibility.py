import xml.etree.ElementTree as ET
from fedora_to_cora.transform.binary.get_binary_visibility import get_binary_visibility
from datetime import datetime
from freezegun import freeze_time


def test_returns_unpublished_when_deleted():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <deleted>true</deleted>
            <deleteDate>2023-01-31T15:41:40.623+01:00</deleteDate>
        </attachment>
        """
    )
    assert get_binary_visibility(source_record) == "unpublished"


@freeze_time("2025-01-01T00:00.000+01:00")
def test_returns_published_when_available_from_in_the_past():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <deleted>false</deleted>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "published"


@freeze_time("2025-01-01T00:00.000+01:00")
def test_returns_unpublished_when_available_from_in_the_future():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2026-12-27T13:23:13.908+01:00</availableFrom>
            <deleted>false</deleted>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


def test_returns_unpublished_when_no_available_from():
    source_record = ET.fromstring(
        """
        <attachment>
            <deleted>false</deleted>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


@freeze_time("2025-01-01T00:00.000+01:00")
def test_returns_published_when_available_from_in_the_past_and_available_until_is_in_the_future():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <availableUntil>2026-12-27T13:23:13.908+01:00</availableUntil>
            <deleted>false</deleted>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "published"


@freeze_time("2027-01-01T00:00.000+01:00")
def test_returns_unpublished_when_available_until_is_in_the_past():

    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <availableUntil>2026-12-27T13:23:13.908+01:00</availableUntil>
            <deleted>false</deleted>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


@freeze_time("2025-01-01T00:00.000+01:00")
def test_returns_unpublished_when_on_hold():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <deleted>false</deleted>
            <onHold>true</onHold>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


def test_returns_unpublished_when_archive_only():

    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <archiveOnly>true</archiveOnly>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


def test_returns_unpublished_when_to_be_archived():

    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <toBeArchived>true</toBeArchived>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


def test_returns_unpublished_when_to_be_published():

    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <toBePublished>true</toBePublished>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"


def test_returns_unpublished_when_print_on_demand():
    source_record = ET.fromstring(
        """
        <attachment>
            <availableFrom>2022-12-27T13:23:13.908+01:00</availableFrom>
            <printOnDemand>true</printOnDemand>
        </attachment>
        """
    )

    assert get_binary_visibility(source_record) == "unpublished"
