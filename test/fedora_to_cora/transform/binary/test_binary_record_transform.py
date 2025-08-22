from fedora_to_cora.transform.binary.binary_record_transform import (
    binary_record_transform,
)
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_binary_record_transform():
    source_record = ET.fromstring(
        """
        <attachment>
            <mimeType>
                <mimeTypeId>62</mimeTypeId>
                <mimeTypeName>application/zip</mimeTypeName>
                <fileSuffix>zip</fileSuffix>
                <datasetOnly>false</datasetOnly>
            </mimeType>
            <fileLabel>
                <fileLabelId>50</fileLabelId>
                <fileLabelCode>fulltext</fileLabelCode>
                <fileLabelNames>
                <fileLabelName>
                    <fileLabelNameId>3674</fileLabelNameId>
                    <locale>no</locale>
                    <fileLabelName>fulltekst</fileLabelName>
                </fileLabelName>
                <fileLabelName>
                    <fileLabelNameId>3651</fileLabelNameId>
                    <locale>sv</locale>
                    <fileLabelName>fulltext</fileLabelName>
                </fileLabelName>
                <fileLabelName>
                    <fileLabelNameId>3650</fileLabelNameId>
                    <locale>en</locale>
                    <fileLabelName>fulltext</fileLabelName>
                </fileLabelName>
                </fileLabelNames>
            </fileLabel>
            <fileName>FULLTEXT01</fileName>
            <fileSize>93598848</fileSize>
            <selectedFileName>BMFEA vol 81</selectedFileName>
            <path>148571d189ed4063c707bb26f397/BMFEA 81_HR + Low (210215).zip</path>
            <checksums>
                <checksum>
                    <type>SHA512</type>
                    <digest>5d516c67a580b689fb27c49b388faf6c50575cdf2a98a1e4b028772801b7f76d1865f24d050dc3d3d835cf23d298f987f8b29c6fd394246b884f0b3554fcd0d4</digest>
                </checksum>
            </checksums>
            <order>1</order>
            <uploadDate>2022-10-13T15:25:10.761+02:00</uploadDate>
            <asyncUpload>false</asyncUpload>
            <availableFrom>2022-10-13T15:25:08.541+02:00</availableFrom>
            <onHold>false</onHold>
            <deleted>false</deleted>
            <prePrint>false</prePrint>
            <postPrint>false</postPrint>
            <print>false</print>
            <archiveOnly>false</archiveOnly>     
        <printOnDemand>false</printOnDemand>
            <toBePublished>false</toBePublished>
            <toBeArchived>false</toBeArchived>
            <digitized>true</digitized>
            <hasCoverPage>false</hasCoverPage>
        </attachment>
        """
    )

    admin = binary_record_transform(source_record)

    assert_equal_for_xml_and_xml_string(
        admin,
        """
            <binary type="generic">
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>genericBinary</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <visibility>published</visibility>
                </recordInfo>
                <originalFileName>BMFEA 81_HR + Low (210215).zip</originalFileName>
                <expectedFileSize>93598848</expectedFileSize>
                <expectedChecksum>5d516c67a580b689fb27c49b388faf6c50575cdf2a98a1e4b028772801b7f76d1865f24d050dc3d3d835cf23d298f987f8b29c6fd394246b884f0b3554fcd0d4</expectedChecksum>
            </binary>
        """,
    )
