from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.series_migrate import series_migrate


@patch("db_to_cora.series_migrate.get_series")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_series_without_relations(mock_create_record, mock_get_series):
    mock_get_series.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>1234</old_id>
                    <title>Some series title</title>
                    <subtitle>Some subtitle</subtitle>
                    <relative_id_host></relative_id_host>
                    <relative_id_preceding></relative_id_preceding>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-series:1234",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-series:1234</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = series_migrate(
        MockContext(), "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <series>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-series</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <permissionUnit>
                        <linkedRecordType>permissionUnit</linkedRecordType>
                        <linkedRecordId>somedomain</linkedRecordId>
                    </permissionUnit>
                    <oldId>1234</oldId>
                </recordInfo>
                <titleInfo>
                    <title>Some series title</title>
                    <subtitle>Some subtitle</subtitle>
                </titleInfo>
            </series>
            """,
    )


@patch("db_to_cora.series_migrate.get_series")
@patch(
    "db_to_cora.records_import.create_record",
)
@patch("db_to_cora.update_relations.update_record")
def test_migrates_a_series_with_relations(
    mock_update_record, mock_create_record, mock_get_series
):
    mock_get_series.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>1</old_id>
                    <title>Child series</title>
                    <subtitle></subtitle>
                    <relative_id_host>2</relative_id_host>
                    <relative_id_preceding>3</relative_id_preceding>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>2</old_id>
                    <title>Host series</title>
                    <subtitle></subtitle>
                    <relative_id_host></relative_id_host>
                    <relative_id_preceding></relative_id_preceding>
                </DATA_RECORD>
                <DATA_RECORD>
                    <domain>somedomain</domain>
                    <old_id>3</old_id>
                    <title>Preceding series</title>
                    <subtitle></subtitle>
                    <relative_id_host></relative_id_host>
                    <relative_id_preceding></relative_id_preceding>
                </DATA_RECORD>
            </SELECT>
    """
    )

    def create_record_side_effect(record, record_type, context):
        old_id = record.findtext(".//oldId")
        return CreateRecordSuccessResult(
            f"diva-series:{old_id}",
            ET.fromstring(
                f"""
                <record>
                    <data>
                        <series>
                            <recordInfo>
                                <id>diva-series:{old_id}</id>
                                <oldId>{old_id}</oldId>
                            </recordInfo>
                        </series>
                    </data> 
                </record>                   
                """
            ),
        )

    mock_create_record.side_effect = create_record_side_effect

    number_of_records = series_migrate(
        MockContext(), "db_user", "db_password", "somedomain"
    )

    assert number_of_records == 3
    assert mock_create_record.call_count == 3
    assert mock_update_record.call_count == 1
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[0].args[0],
        """
        <series>
            <recordInfo>
                <id>diva-series:1</id>
                <oldId>1</oldId>
            </recordInfo>
            <related type="host" repeatId="0">
                <topic>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:2</linkedRecordId>
                </topic>
            </related>
            <related type="preceding" repeatId="0">
                <topic>
                    <linkedRecordType>diva-series</linkedRecordType>
                    <linkedRecordId>diva-series:3</linkedRecordId>
                </topic>
            </related>
        </series>
    """,
    )
