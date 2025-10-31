import pytest
from xml.etree import ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from fedora_to_cora.transform.create_title_info import _create_title_info


def test_create_title_info():
    source_record = ET.fromstring(
        """
      <publication>
          <originalPublicationTitle>
              <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
              <subTitle></subTitle>
              <language>
                  <languageCode3>eng</languageCode3>
              </language>
          </originalPublicationTitle>
      </publication>
  """
    )
    title_info = _create_title_info(source_record)

    assert_equal_for_xml_and_xml_string(
        title_info,
        """
      <titleInfo lang="eng">
          <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
      </titleInfo>
  """,
    )


def test_create_title_info_with_subtitle():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
                <subTitle>subtitle</subTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )
    title_info = _create_title_info(source_record_with_subtitle)

    assert_equal_for_xml_and_xml_string(
        title_info,
        """
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            <subtitle>subtitle</subtitle>
        </titleInfo>
    """,
    )


def test_create_title_info_missing_title():
    source_record = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    assert _create_title_info(source_record) is None


def test_create_title_info_missing_language():
    source_record_with_subtitle = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            </originalPublicationTitle>
        </publication>
    """
    )

    assert _create_title_info(source_record_with_subtitle) is None


def test_create_title_with_html():
    source_record_with_html = ET.fromstring(
        """
        <publication>
            <originalPublicationTitle>
                <title>&lt;p&gt;Bulletin of the &lt;i&gt;Museum&lt;/i&gt; of Far Eastern Antiquities (BMFEA)&lt;/p&gt;</title>
                <subTitle>&lt;p&gt;A subtitle&lt;/p&gt;</subTitle>
                <language><languageCode3>eng</languageCode3></language>
            </originalPublicationTitle>
        </publication>
    """
    )

    title_info = _create_title_info(source_record_with_html)
    assert_equal_for_xml_and_xml_string(
        title_info,
        """
        <titleInfo lang="eng">
            <title>Bulletin of the Museum of Far Eastern Antiquities (BMFEA)</title>
            <subtitle>A subtitle</subtitle>
        </titleInfo>
    """,
    )
