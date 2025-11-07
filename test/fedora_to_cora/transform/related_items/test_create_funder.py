import xml.etree.ElementTree as ET
from cora.context import MockContext
from fedora_to_cora.transform.related_items.create_funder import (
    create_related_item_type_funder,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from unittest.mock import patch


def test_create_funder_link():
    pass


@patch("fedora_to_cora.transform.related_items.create_funder.get_cora_id_by_old_id")
def test_create_funder_with_project_id(mock_get_cora_id_by_old_id):
    mock_get_cora_id_by_old_id.return_value = "funder:2"

    source_record = ET.fromstring(
        """
        <publication>
            <funderInfos>
                <funderInfo>
                    <funder>
                        <funderId>2</funderId>
                        <funderName>
                        <name>Vetenskapsrådet</name>
                        <locale>sv</locale>
                        </funderName>
                        <organisationNumber>202100-5208</organisationNumber>
                        <funderAlternativeNames>
                        <diva2.commons.aura.list.funder.FunderName>
                            <funderNameId>2</funderNameId>
                            <locale>en</locale>
                            <funderName>Swedish Research Council</funderName>
                        </diva2.commons.aura.list.funder.FunderName>
                        </funderAlternativeNames>
                        <doi>10.13039/501100004359</doi>
                    </funder>
                    <projectNumber>2021-00001</projectNumber>
                </funderInfo>
            </funderInfos>
        </publication>
        """
    )
    result = create_related_item_type_funder(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        result[0],
        """
        <relatedItem type="funder" repeatId="0">
            <funder>
                <linkedRecordType>diva-funder</linkedRecordType>
                <linkedRecordId>funder:2</linkedRecordId>
            </funder>
            <identifier type="project">2021-00001</identifier>
        </relatedItem>
        """,
    )


def test_create_no_funder_infos():
    source_record = ET.fromstring("""<publication></publication>""")
    result = create_related_item_type_funder(source_record, MockContext())
    assert len(result) == 0


def test_create_empty_funder_infos():
    source_record = ET.fromstring(
        """<publication><funderInfos></funderInfos></publication>"""
    )
    result = create_related_item_type_funder(source_record, MockContext())
    assert len(result) == 0


def test_create_empty_funder_info():
    source_record = ET.fromstring(
        """<publication><funderInfos><funderInfo></funderInfo></funderInfos></publication>"""
    )
    result = create_related_item_type_funder(source_record, MockContext())
    assert len(result) == 0
