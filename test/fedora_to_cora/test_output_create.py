from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.output_create import transform_to_cora_output
from xml.etree import ElementTree as ET
from common.common_data import read_source_xml


def test_creates_output():
    fedora_xml = read_source_xml("data/fedora_xml/1681782_varldskulturmuserna.xml")

    result = transform_to_cora_output(fedora_xml)

    expected_xml = """
    <output>
        <recordInfo>
            <validationType>publication_edited-book</validationType>
            <dataDivider>divaData</dataDivider>
            <permissionUnit>
            <linkedRecordType>permissionUnit</linkedRecordType>
            <linkedRecordId>varldskulturmuseerna</linkedRecordId>
            </permissionUnit>
            <visibility>published</visibility>
            <oldId>diva2:1681782</oldId>
        </recordInfo>
        <genre type="contentType">ref</genre>
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
        </titleInfo>
        <subject lang="eng">
            <topic>Sinologi, Arkeologi</topic>
        </subject>
        <genre type="outputType">publication_edited-book</genre>
        <language repeatId="0">
            <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
        </language>
        <artisticWork type="outputType">false</artisticWork>
        <name repeatId="0" type="personal">
            <namePart type="family">Östasiatiska museet</namePart>
            <namePart type="given">Östasiatiska museet</namePart>
            <role>
                <roleTerm repeatId="0" type="code">edt</roleTerm>
            </role>
            <affiliation repeatId="0"></affiliation>
        </name>
    </output>
    """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
