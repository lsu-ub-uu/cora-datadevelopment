import xml.etree.ElementTree as ET
from unittest.mock import patch
from classic.get_series import get_series
from common.test_helper import assert_equal_for_sql


@patch("classic.get_series.execute_sql")
def test_get_series(mock_execute_sql):
    expected_query = """
SELECT
    s.domain,
    s.series_id as old_id,
    st.main_title as title,
    st.sub_title as subtitle,
    sat.main_title as alternative_title,
    sat.sub_title as alternative_subtitle,
    s.closed_date as end_date,
    s.issn as identifier_pissn,
    s.eissn as identifier_eissn,
    s.format_id,
    f.format_code,
    s.url,
    s.notes as internal_note,
    s.publication_type_id,
    pt.publication_type_code,
    string_agg(srp.relative_id::text, ',') as relative_id_host,
    srp.series_id,
    string_agg(sre.relative_id::text, ',') as relative_id_preceding,
    sre.series_id,
    s.organisation_id
FROM
    series s
    left join series_title st on s.series_id = st.series_id
    left join series_alternative_title sat on s.series_id = sat.series_id
    left join format f on s.format_id = f.format_id
    left join series_relation srp on s.series_id = srp.series_id
    and srp.relation_type_id = '52'
    left join series_relation sre on s.series_id = sre.series_id
    and sre.relation_type_id = '50'
    left join publication_type pt on s.publication_type_id = pt.publication_type_id --borde_vara_string_agg?
WHERE
    s.domain = %(domain)s
GROUP BY
    s.domain,
    s.series_id,
    st.main_title,
    st.sub_title,
    sat.main_title,
    sat.sub_title,
    s.closed_date,
    s.issn,
    s.eissn,
    s.format_id,
    f.format_code,
    s.url,
    s.notes,
    s.publication_type_id,
    pt.publication_type_code,
    srp.relation_type_id,
    srp.relative_id,
    srp.series_id,
    sre.relation_type_id,
    sre.series_id,
    s.organisation_id;
"""

    mock_series = ET.Element("series")
    mock_execute_sql.return_value = mock_series

    result = get_series(
        domain="norden", db_user="test_user", db_password="test_password"
    )

    assert result == mock_series
    mock_execute_sql.assert_called_once()

    assert_equal_for_sql(mock_execute_sql.mock_calls[0].args[0], expected_query)
    assert mock_execute_sql.mock_calls[0].kwargs["params"] == {"domain": "norden"}
    assert mock_execute_sql.mock_calls[0].kwargs["db_user"] == "test_user"
    assert mock_execute_sql.mock_calls[0].kwargs["db_password"] == "test_password"
