import xml.etree.ElementTree as ET
from unittest.mock import patch
from classic.get_programmes import get_programmes
from common.test_helper import assert_equal_for_sql


@patch("classic.get_programmes.execute_sql")
def test_get_programmes(mock_execute_sql):
    expected_query = """
SELECT
    s.domain,
    s.subject_id as old_id,
    s.closed_date as end_date,
    sn_swe.subject_name as name_swe,
    sn_eng.subject_name as name_eng,
    string_agg(sp.subject_id::text, ',') as broader_id,
    string_agg(pre.subject_id::text, ',') as earlier_id
FROM
    subject s
    left join subject_name sn_swe on s.subject_id = sn_swe.subject_id
    and sn_swe.locale = 'sv'
    left join subject_name sn_eng on s.subject_id = sn_eng.subject_id
    and sn_eng.locale = 'en'
    left join subject_parent sp on s.subject_id = sp.parent_subject_id
    left join subject_predecessor pre on s.subject_id = pre.predecessor_subject_id
WHERE
    s.subject_type_id = %(subject_type_id)s
    and s.domain = %(domain)s
GROUP BY
    s.domain,
    s.subject_id,
    s.closed_date,
    sn_swe.subject_name,
    sn_eng.subject_name;
"""

    mock_programme = ET.Element("programme")
    mock_execute_sql.return_value = mock_programme

    result = get_programmes(
        domain="norden", db_user="test_user", db_password="test_password"
    )

    assert result == mock_programme
    mock_execute_sql.assert_called_once()

    assert_equal_for_sql(mock_execute_sql.mock_calls[0].args[0], expected_query)
    assert mock_execute_sql.mock_calls[0].kwargs["params"] == {
        "domain": "norden",
        "subject_type_id": "56",
    }
    assert mock_execute_sql.mock_calls[0].kwargs["db_user"] == "test_user"
    assert mock_execute_sql.mock_calls[0].kwargs["db_password"] == "test_password"
