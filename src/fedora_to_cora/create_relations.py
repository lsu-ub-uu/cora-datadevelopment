from fedora_to_cora.output_migration_result import OutputRelation
import xml.etree.ElementTree as ET


def create_relations(source_record: ET.Element) -> list[OutputRelation]:
    constituent_relations = _create_constituent_relations(source_record)
    related_relations = _create_related_relations(source_record)
    return constituent_relations + related_relations


def _create_constituent_relations(source_record: ET.Element) -> list[OutputRelation]:
    return [
        OutputRelation(type="constituent", pid=pid)
        for part in source_record.findall(".//partsOfPublication/publication")
        if (pid := part.findtext("pid"))
    ]


def _create_related_relations(source_record: ET.Element) -> list[OutputRelation]:
    return [
        OutputRelation(type="related", pid=pid)
        for host in source_record.findall(".//hostPublications/hostPublication")
        if (pid := host.findtext("pid"))
    ]
