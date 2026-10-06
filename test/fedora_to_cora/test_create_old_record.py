import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.create_old_record import create_old_record


def test_create_old_record():
    pid = "12345"
    source_record = f"""<record>
    <pid>{pid}</pid>
    <publicationType>
        <publicationTypeCode>journal</publicationTypeCode>
    </publicationType>
</record>"""

    cora_record = create_old_record(ET.fromstring(source_record))
    assert_equal_for_xml_and_xml_string(
        cora_record.find("./recordInfo"),
        f"""
        <recordInfo>
            <id>{pid}</id>
            <validationType>
                <linkedRecordType>validationType</linkedRecordType>
                <linkedRecordId>diva-oldRecord</linkedRecordId>
            </validationType>
            <dataDivider>
                <linkedRecordType>system</linkedRecordType>
                <linkedRecordId>divaData</linkedRecordId>
            </dataDivider>
            <oldId>{pid}</oldId>
        </recordInfo>""",
    )
    assert cora_record.findtext("./recordXml") == (
        f"<![CDATA[<record>   <pid>{pid}</pid>   <publicationType> "
        "    <publicationTypeCode>journal</publicationTypeCode>   "
        "</publicationType> </record>]]>"
    )
