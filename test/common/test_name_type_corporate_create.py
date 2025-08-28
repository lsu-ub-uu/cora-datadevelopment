from common.common_data import name_type_corporate_create
from common.test_helper import assert_equal_for_xml_and_xml_string


def test_name_type_corporate_create():
    result = name_type_corporate_create("Some Name")

    expected_xml = """
        <name type="corporate">
            <namePart>Some Name</namePart>
        </name>
        """

    assert_equal_for_xml_and_xml_string(result, expected_xml)
