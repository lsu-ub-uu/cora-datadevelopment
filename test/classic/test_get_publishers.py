import xml.etree.ElementTree as ET
from unittest.mock import patch
from classic.get_publishers import get_publishers
from common.test_helper import assert_equal_for_sql


@patch("classic.get_publishers.execute_sql")
def test_get_publishers(mock_execute_sql):
    expected_query = """
SELECT
	p.publishing_house_id as old_id,
	p.name
FROM
	publishing_house p
"""

    mock_publishers = ET.Element("PUBLISHERS")
    mock_execute_sql.return_value = mock_publishers

    result = get_publishers(
        db_host="localhost", db_port=5432, db_name="auradb",
        db_user="test_user", db_password="test_password",
    )

    assert result == mock_publishers
    mock_execute_sql.assert_called_once()

    assert_equal_for_sql(mock_execute_sql.mock_calls[0].args[0], expected_query)
    assert mock_execute_sql.mock_calls[0].kwargs["db_host"] == "localhost"
    assert mock_execute_sql.mock_calls[0].kwargs["db_port"] == 5432
    assert mock_execute_sql.mock_calls[0].kwargs["db_name"] == "auradb"
    assert mock_execute_sql.mock_calls[0].kwargs["db_user"] == "test_user"
    assert mock_execute_sql.mock_calls[0].kwargs["db_password"] == "test_password"
