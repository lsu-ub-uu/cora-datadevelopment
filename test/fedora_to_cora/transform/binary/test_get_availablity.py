import xml.etree.ElementTree as ET

import pytest
from unittest.mock import patch

from fedora_to_cora.transform.binary.get_availability import get_availablity

def test_returns_unavaiable_when_no_flag_is_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>false</toBePublished>
            <toBeArchived>false</toBeArchived>
            <secrecyInfo>
                <secrecy>false</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "unavailable"

def test_returns_available_when_to_be_published_is_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>true</toBePublished>
            <toBeArchived>false</toBeArchived>
            <secrecyInfo>
                <secrecy>false</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "available"

def test_returns_unavaible_when_to_be_archived_is_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>false</toBePublished>
            <toBeArchived>true</toBeArchived>
            <secrecyInfo>
                <secrecy>false</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "unavailable"

def test_returns_secrecy_when_secrecy_is_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>false</toBePublished>
            <toBeArchived>false</toBeArchived>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "secrecy"

def test_returns_secrecy_when_all_flags_are_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>true</toBePublished>
            <toBeArchived>true</toBeArchived>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "secrecy"

def test_returns_unavaible_when_to_be_archived_and_to_be_published_are_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>true</toBePublished>
            <toBeArchived>true</toBeArchived>
            <secrecyInfo>
                <secrecy>false</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "unavailable"
    
def test_returns_secrecy_when_secrecy_and_to_be_published_are_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>true</toBePublished>
            <toBeArchived>false</toBeArchived>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "secrecy"
    

def test_returns_secrecy_when_secrecy_and_to_be_archived_are_true():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>false</toBePublished>
            <toBeArchived>true</toBeArchived>
            <secrecyInfo>
                <secrecy>true</secrecy>
            </secrecyInfo>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "secrecy"

def test_handles_missing_secrecy_info():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>true</toBePublished>
            <toBeArchived>false</toBeArchived>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "available"

def test_returns_available_when_no_secrecy_and_binary_visibility_is_published():
    source_attachment = ET.fromstring(
        """
        <attachment>
            <toBePublished>false</toBePublished>
            <toBeArchived>false</toBeArchived>
            <secrecyInfo>
                <secrecy>false</secrecy>
            </secrecyInfo>
            <availableFrom>2020-01-01T00:00:00+00:00</availableFrom>
        </attachment>
        """
    )

    availability = get_availablity(source_attachment)
    assert availability == "available"