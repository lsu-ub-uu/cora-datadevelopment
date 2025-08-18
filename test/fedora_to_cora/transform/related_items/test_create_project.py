import xml.etree.ElementTree as ET
from fedora_to_cora.transform.related_items.create_project import (
    create_related_item_type_project,
)
from common.test_helper import assert_equal_for_xml_and_xml_string
from cora.context import MockContext


def test_create_controlled_project_link(monkeypatch):
    project_old_id_1 = "17450"
    project_old_id_2 = "17451"
    project_cora_id_1 = "diva-project:17450"
    project_cora_id_2 = "diva-project:17451"

    def get_cora_id_by_old_id_mock(old_id, *args, **kwargs):
        if old_id == project_old_id_1:
            return project_cora_id_1
        elif old_id == project_old_id_2:
            return project_cora_id_2
        else:
            raise ValueError(f"Unexpected old ID: {old_id}")

    monkeypatch.setattr(
        "fedora_to_cora.transform.related_items.create_project.get_cora_id_by_old_id",
        get_cora_id_by_old_id_mock,
    )

    source_record = ET.fromstring(
        f"""
        <publication>
             <projectRelations>
                <projectRelation>
                    <pid>{project_old_id_1}</pid>
                </projectRelation>
                <projectRelation>
                    <pid>{project_old_id_2}</pid>
                </projectRelation>
            </projectRelations>
        </publication>
        """
    )

    project_item = create_related_item_type_project(source_record, MockContext())

    assert_equal_for_xml_and_xml_string(
        project_item[0],
        f"""
        <relatedItem type="project" repeatId="controlled0">
            <project>
                <linkedRecordType>diva-project</linkedRecordType>
                <linkedRecordId>{project_cora_id_1}</linkedRecordId>
            </project>
        </relatedItem>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        project_item[1],
        f"""
        <relatedItem type="project" repeatId="controlled1">
            <project>
                <linkedRecordType>diva-project</linkedRecordType>
                <linkedRecordId>{project_cora_id_2}</linkedRecordId>
            </project>
        </relatedItem>
        """,
    )


def test_create_uncontrolled_project():
    source_record = ET.fromstring(
        """
        <publication>
            <projects>
                <project>
                    <projectName>Ett annat projekt</projectName>
                </project>
                <project>
                    <projectName>Ytterligare ett annat projekt</projectName>
                </project>
            </projects>
        </publication>
        """
    )
    project = create_related_item_type_project(source_record, MockContext())

    assert len(project) == 2
    assert_equal_for_xml_and_xml_string(
        project[0],
        """
        <relatedItem type="project" repeatId="uncontrolled0">
            <titleInfo>
                <title>Ett annat projekt</title>
            </titleInfo>
        </relatedItem>
        """,
    )
    assert_equal_for_xml_and_xml_string(
        project[1],
        """
        <relatedItem type="project" repeatId="uncontrolled1">
            <titleInfo>
                <title>Ytterligare ett annat projekt</title>
            </titleInfo>
        </relatedItem>
        """,
    )
