from cora.get_organisation_by_old_id import get_organisation_id_by_old_id
from common.xml_utils import inline_xml_string


def test_get_organisation_by_old_id(requests_mock):
    base_url = "https://pre.diva-portal.org/rest/record/"
    old_id = "878550"
    test_token = "test-token"
    expected_cora_id = "123"

    expected_search_data = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <search>
            <include>
                <includePart>
                    <oldIdSearchTerm>{old_id}</oldIdSearchTerm>
                </includePart>
            </include>
        </search>
    """

    mock_response = f"""
        <dataList>
            <data>
                <record>
                    <data>
                        <organisation>
                            <recordInfo>
                                <id>{expected_cora_id}</id>
                            </recordInfo>
                        </organisation>
                    </data>
                </record>
            </data>
        </dataList>
    """
    print(
        f"inline_xml_string(expected_search_data): {inline_xml_string(expected_search_data)}"
    )

    requests_mock.get(
        f"https://pre.diva-portal.org/rest/record/searchResult/diva-organisationSearch?searchData={inline_xml_string(expected_search_data)}",
        request_headers={"Authtoken": test_token},
        text=mock_response,
    )
    response = get_organisation_id_by_old_id(
        old_id, base_url=base_url, auth_token=test_token
    )
    assert response == expected_cora_id
