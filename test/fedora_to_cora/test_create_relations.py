import xml.etree.ElementTree as ET

from fedora_to_cora.create_relations import create_relations
from fedora_to_cora.output_migration_result import OutputRelation


def test_create_constituent_relation():
    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Test Publication</title>
            <partsOfPublication>
                <publication>
                    <pid>diva2:67890</pid>
                    <title>Part of Test Publication</title>
                </publication>
            </partsOfPublication>
        </publication>
        """)

    relations = create_relations(source_record)

    assert len(relations) == 1
    assert relations[0].pid == "diva2:67890"
    assert relations[0].type == "constituent"


def test_create_related_relation():
    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:12345</pid>
            <title>Part of Test Publication</title>
            <hostPublications>
                <hostPublication>
                    <pid>diva2:67890</pid>
                    <title>Test Publication</title>
                </hostPublication>
            </hostPublications>
        </publication>
        """)

    relations = create_relations(source_record)

    assert len(relations) == 1
    assert relations[0].pid == "diva2:67890"
    assert relations[0].type == "related"


def test_create_multiple_relations():
    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:111111</pid>
            <title>Test Publication</title>
            <partsOfPublication>
                <publication>
                    <pid>diva2:22222</pid>
                    <title>Part of Test Publication</title>
                </publication>
                 <publication>
                    <pid>diva2:33333</pid>
                    <title>Part of Test Publication</title>
                </publication>
            </partsOfPublication>
            <hostPublications>
                <hostPublication>
                    <pid>diva2:44444</pid>
                    <title>Another Test Publication</title>
                </hostPublication>
                 <hostPublication>
                    <pid>diva2:55555</pid>
                    <title>Another Test Publication</title>
                </hostPublication>
            </hostPublications>
        </publication>
        """)

    relations = create_relations(source_record)

    assert len(relations) == 4
    assert relations[0].pid == "diva2:22222"
    assert relations[0].type == "constituent"
    assert relations[1].pid == "diva2:33333"
    assert relations[1].type == "constituent"
    assert relations[2].pid == "diva2:44444"
    assert relations[2].type == "related"
    assert relations[3].pid == "diva2:55555"
    assert relations[3].type == "related"


def test_create_no_relations():
    source_record = ET.fromstring("""
        <publication>
            <pid>diva2:111111</pid>
            <title>Test Publication</title>
        </publication>
        """)

    relations = create_relations(source_record)

    assert len(relations) == 0
