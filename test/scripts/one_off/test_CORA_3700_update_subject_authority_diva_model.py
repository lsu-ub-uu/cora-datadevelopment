from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext
from scripts.one_off.CORA_3700_update_subject_authority_diva_model import fix_records


@patch("scripts.one_off.CORA_3700_update_subject_authority_diva_model.list_records")
@patch("scripts.one_off.CORA_3700_update_subject_authority_diva_model.update_record")
@patch("scripts.one_off.CORA_3700_update_subject_authority_diva_model.run_with_threads")
def test_updates_outputs_with_subject_authority_diva(
    mock_run_with_threads, mock_update_record, mock_list_records
):
    mock_run_with_threads.side_effect = lambda iterable, function, *args: [
        function(item) for item in iterable
    ]

    mock_list_records.return_value = [
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-one-subject</id>
                        </recordInfo>
                        <subject authority="diva">
                            <topic repeatId="0">
                                <linkedRecordType>diva-subject</linkedRecordType>
                                <linkedRecordId>456</linkedRecordId>
                            </topic>    
                        </subject>
                    </output>
                </data>
            </record>
        """),
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-two-subjects</id>
                        </recordInfo>
                        <subject authority="diva">
                            <topic repeatId="0">
                                <linkedRecordType>diva-subject</linkedRecordType>
                                <linkedRecordId>456</linkedRecordId>
                            </topic>   
                            <topic repeatId="1">
                                <linkedRecordType>diva-subject</linkedRecordType>
                                <linkedRecordId>789</linkedRecordId>
                            </topic>     
                        </subject>
                    </output>
                </data>
            </record>
        """),
        ET.fromstring("""
            <record>
                <data>
                    <output>
                        <recordInfo>
                            <id>output-with-no-subjects</id>
                        </recordInfo>
                    </output>
                </data>
            </record>
        """),
    ]

    fix_records(Mock(), MockContext())

    assert mock_update_record.call_count == 2

    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[0].args[0],
        """
                <record>
                    <data>
                        <output>
                            <recordInfo>
                                <id>output-with-one-subject</id>
                            </recordInfo>
                            <subject authority="diva" repeatId="0">
                                <topic>
                                    <linkedRecordType>diva-subject</linkedRecordType>
                                    <linkedRecordId>456</linkedRecordId>
                                </topic>    
                            </subject>
                        </output>
                    </data>
                </record>
            """,
    )
    assert_equal_for_xml_and_xml_string(
        mock_update_record.call_args_list[1].args[0],
        """
                <record>
                    <data>
                        <output>
                            <recordInfo>
                                <id>output-with-two-subjects</id>
                            </recordInfo>
                            <subject authority="diva" repeatId="0">
                                <topic>
                                    <linkedRecordType>diva-subject</linkedRecordType>
                                    <linkedRecordId>456</linkedRecordId>
                                </topic>    
                            </subject>
                            <subject authority="diva" repeatId="1">
                                <topic>
                                    <linkedRecordType>diva-subject</linkedRecordType>
                                    <linkedRecordId>789</linkedRecordId>
                                </topic>    
                            </subject>
                        </output>
                    </data>
                </record>
                """,
    )
