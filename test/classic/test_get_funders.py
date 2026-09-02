import xml.etree.ElementTree as ET
from unittest.mock import patch
from classic.get_funders import get_funders
from common.test_helper import assert_equal_for_sql


@patch("classic.get_funders.execute_sql")
def test_get_funders(mock_execute_sql):
    expected_query = """
SELECT
	f.funder_id as old_id,
	f.funder_name as name_swe,
	fn.funder_name as name_eng,
	f.closed_date as end_date,
	f.orgnumber as "identifier_organisationNumber",
	f.doi as identifier_doi,
	f.funder_name_locale as locale_swe,
	fn.locale as locale_eng,
	fn.funder_name_id
FROM
	funder f
	left join funder_name fn on f.funder_id = fn.funder_id
"""

    mock_funders = ET.Element("FUNDERS")
    mock_execute_sql.return_value = mock_funders

    result = get_funders(
        db_host="localhost", db_port=5432, db_name="auradb",
        db_user="test_user", db_password="test_password",
    )

    assert result == mock_funders
    mock_execute_sql.assert_called_once()

    assert_equal_for_sql(mock_execute_sql.mock_calls[0].args[0], expected_query)
    assert mock_execute_sql.mock_calls[0].kwargs["db_user"] == "test_user"
    assert mock_execute_sql.mock_calls[0].kwargs["db_password"] == "test_password"
