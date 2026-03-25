from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from cora.create import CreateRecordSuccessResult
from db_to_cora.journals_migrate import journals_migrate


@patch("db_to_cora.journals_migrate.get_journals")
@patch(
    "db_to_cora.records_import.create_record",
)
def test_migrate_a_journal(mock_create_record, mock_get_journals):
    mock_get_journals.return_value = ET.fromstring(
        """
            <SELECT>
                <DATA_RECORD>
                    <old_id>1234</old_id>
                    <title>Some journal title</title>
                    <subtitle>Some subtitle</subtitle>
                </DATA_RECORD>
            </SELECT>
    """
    )

    mock_create_record.return_value = CreateRecordSuccessResult(
        "diva-journal:1234",
        ET.fromstring(
            """
              <record>
                <data>
                    <recordInfo>
                        <id>diva-journal:1234</id>
                    </recordInfo>
                </data> 
              </record>                   
            """
        ),
    )

    number_of_records = journals_migrate(MockContext(), "db_user", "db_password")

    assert number_of_records == 1
    mock_create_record.assert_called_once()
    created_record = mock_create_record.call_args.args[0]

    assert_equal_for_xml_and_xml_string(
        created_record,
        """
            <journal>
                <recordInfo>
                    <validationType>
                        <linkedRecordType>validationType</linkedRecordType>
                        <linkedRecordId>diva-journal</linkedRecordId>
                    </validationType>
                    <dataDivider>
                        <linkedRecordType>system</linkedRecordType>
                        <linkedRecordId>divaData</linkedRecordId>
                    </dataDivider>
                    <oldId>1234</oldId>
                </recordInfo>
                <titleInfo>
                    <title>Some journal title</title>
                    <subtitle>Some subtitle</subtitle>
                </titleInfo>
            </journal>
            """,
    )
