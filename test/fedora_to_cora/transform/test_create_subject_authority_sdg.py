import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_subject_authority_sdg import (
    create_subject_authority_sdg,
)
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_subject_authority_sdg():
    source_record = ET.fromstring(
        """
       <publication>
            <sustainableDevelopments>
                <sustainableDevelopment>
                    <developmentId>850</developmentId>
                </sustainableDevelopment>
            </sustainableDevelopments>
        </publication>
        """
    )

    subject = create_subject_authority_sdg(source_record)

    assert_equal_for_xml_and_xml_string(
        subject,
        """
        <subject authority="sdg">
            <topic repeatId="0">sdg1</topic>
        </subject>
        """,
    )


def test_create_subject_authority_sdg_none():
    source_record = ET.fromstring(
        """
       <publication>
            <sustainableDevelopments>
                <sustainableDevelopment>
                </sustainableDevelopment>
            </sustainableDevelopments>
        </publication>
        """
    )

    subject = create_subject_authority_sdg(source_record)

    assert subject is None


def test_create_subject_authority_sdg_all():
    source_record = ET.fromstring(
        """
       <publication>
            <sustainableDevelopments>
                <sustainableDevelopment>
                    <developmentId>801</developmentId>
                </sustainableDevelopment>
            </sustainableDevelopments>
        </publication>
        """
    )

    subject = create_subject_authority_sdg(source_record)

    assert_equal_for_xml_and_xml_string(
        subject,
        """
        <subject authority="sdg">
            <topic repeatId="0">sdg1</topic>
            <topic repeatId="1">sdg2</topic>
            <topic repeatId="2">sdg3</topic>
            <topic repeatId="3">sdg4</topic>
            <topic repeatId="4">sdg5</topic>
            <topic repeatId="5">sdg6</topic>
            <topic repeatId="6">sdg7</topic>
            <topic repeatId="7">sdg8</topic>
            <topic repeatId="8">sdg9</topic>
            <topic repeatId="9">sdg10</topic>
            <topic repeatId="10">sdg11</topic>
            <topic repeatId="11">sdg12</topic>
            <topic repeatId="12">sdg13</topic>
            <topic repeatId="13">sdg14</topic>
            <topic repeatId="14">sdg15</topic>
            <topic repeatId="15">sdg16</topic>
            <topic repeatId="16">sdg17</topic>
        </subject>
        """,
    )


def test_create_subject_authority_sdg_with_text():
    source_record = ET.fromstring(
        """
       <publication>
            <sustainableDevelopments>
                <sustainableDevelopment>
                    <developmentId>150</developmentId>
                </sustainableDevelopment>
            </sustainableDevelopments>
        </publication>
        """
    )

    subject = create_subject_authority_sdg(source_record)

    assert_equal_for_xml_and_xml_string(
        subject,
        """
    <subject authority="sdg">
        <topic repeatId="0">Uppsatsen/examensarbetet handlar till övervägande del om hållbar utveckling enligt högskolans kriterier</topic>
    </subject>
    """,
    )


def test_create_subject_authority_sdg_filters_duplicates_when_all_and_one_more():
    # 801 = all sdgs
    # 818 = sdg16
    source_record = ET.fromstring(
        """
       <publication>
            <sustainableDevelopments>
                <sustainableDevelopment>
                    <developmentId>801</developmentId>
                </sustainableDevelopment>
                <sustainableDevelopment>
                    <developmentId>818</developmentId>
                </sustainableDevelopment>
            </sustainableDevelopments>
        </publication> 
        """
    )

    subject = create_subject_authority_sdg(source_record)

    assert_equal_for_xml_and_xml_string(
        subject,
        """
        <subject authority="sdg">
            <topic repeatId="0">sdg1</topic>
            <topic repeatId="1">sdg2</topic>
            <topic repeatId="2">sdg3</topic>
            <topic repeatId="3">sdg4</topic>
            <topic repeatId="4">sdg5</topic>
            <topic repeatId="5">sdg6</topic>
            <topic repeatId="6">sdg7</topic>
            <topic repeatId="7">sdg8</topic>
            <topic repeatId="8">sdg9</topic>
            <topic repeatId="9">sdg10</topic>
            <topic repeatId="10">sdg11</topic>
            <topic repeatId="11">sdg12</topic>
            <topic repeatId="12">sdg13</topic>
            <topic repeatId="13">sdg14</topic>
            <topic repeatId="14">sdg15</topic>
            <topic repeatId="15">sdg16</topic>
            <topic repeatId="16">sdg17</topic>
        </subject>
        """,
    )
