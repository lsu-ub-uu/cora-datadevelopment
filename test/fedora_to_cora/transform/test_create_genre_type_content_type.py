from xml.etree import ElementTree as ET
from fedora_to_cora.transform.create_genre_type_content_type import (
    create_genre_type_content_type,
)

source_record = ET.fromstring(
    """
    <publication>
        <contentType>
            <contentTypeCode>refereed</contentTypeCode>
        </contentType>
    </publication>
    """
)

class TestCreateGenreTypeContentType:
    def test_create_genre_type_content_type(self):
        contentType = create_genre_type_content_type(source_record)
        assert contentType is not None
        assert contentType.tag == "genre"
        assert contentType.attrib["type"] == "contentType"
        assert contentType.text == "ref"

    def test_create_genre_type_content_type_missing(self):
        source_record = ET.fromstring(
            """
        <publication>
        </publication>
        """
        )
        contentType = create_genre_type_content_type(source_record)
        assert contentType is None
