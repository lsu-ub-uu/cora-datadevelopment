import xml.etree.ElementTree as ET
from unittest.mock import patch
from classic.get_journals import get_journals
from common.test_helper import assert_equal_for_sql


@patch("classic.get_journals.execute_sql")
def test_get_journals(mock_execute_sql):
    expected_query = """
SELECT
	j.journal_id AS old_id,
	jt.main_title AS title,
	jt.sub_title AS subtitle,
	j.closed_date AS end_date,
	j.eissn AS identifier_eissn,
	j.issn AS identifier_pissn,
	j.url
FROM
	journal j
	LEFT JOIN journal_title jt ON j.journal_id = jt.journal_id
"""

    mock_journals = ET.Element("JOURNALS")
    mock_execute_sql.return_value = mock_journals

    result = get_journals(db_user="test_user", db_password="test_password")

    assert result == mock_journals
    mock_execute_sql.assert_called_once()

    assert_equal_for_sql(mock_execute_sql.mock_calls[0].args[0], expected_query)
    assert mock_execute_sql.mock_calls[0].kwargs["db_user"] == "test_user"
    assert mock_execute_sql.mock_calls[0].kwargs["db_password"] == "test_password"
