import xml.etree.ElementTree as ET
from fedora_to_cora.transform.create_abstracts import create_abstracts
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_create_abstracts():
    source_record = ET.fromstring(
        """
        <publication>
            <abstracts>
                <abstract>
                    <language>
                        <languageCode3>swe</languageCode3>
                    </language>
                    <text>Lorem ipsum dolor sit amet</text>
                </abstract>
                <abstract>
                    <language>
                        <languageCode3>eng</languageCode3>
                    </language>
                    <text>
                        &lt;p&gt;Another summary, &lt;strong&gt;bold text&lt;/strong&gt;, &lt;em&gt;cursive text,&lt;/em&gt; &lt;sup&gt;to the power of text&lt;/sup&gt;,&lt;sub&gt;subscript text&lt;/sub&gt;&lt;/p&gt;&lt;p&gt;&lt;p&gt;Another paragraph.&lt;/p&gt;
                    </text>
                    </abstract>
                </abstracts>
        </publication>
        """
    )

    abstracts = create_abstracts(source_record)

    assert_equal_for_xml_and_xml_string(
        abstracts[0],
        """
        <abstract lang="swe" repeatId="0">
           Lorem ipsum dolor sit amet
        </abstract>
        """,
    )

    assert_equal_for_xml_and_xml_string(
        abstracts[1],
        """
        <abstract lang="eng" repeatId="1">
            Another summary, bold text, cursive text, to the power of text,subscript text\n\nAnother paragraph.
        </abstract>
        """,
    )


def test_create_abstracts_empty():
    source_record = ET.fromstring(
        """
        <publication>
            <abstracts>
                <abstract>
                    <language>
                        <languageCode3>swe</languageCode3>
                    </language>
                </abstract>
            </abstracts>
        </publication>
        """
    )

    abstracts = create_abstracts(source_record)

    assert len(abstracts) == 0
