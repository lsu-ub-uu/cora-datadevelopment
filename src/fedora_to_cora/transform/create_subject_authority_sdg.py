import xml.etree.ElementTree as ET
from fedora_to_cora.transform.get_sdg import get_sdg


def create_subject_authority_sdg(source_record: ET.Element) -> ET.Element:
    """
    Create a subject element with authority "sdg" based on the source record.
    """
    subject = ET.Element("subject", authority="sdg")

    development_ids = source_record.findall(
        "./sustainableDevelopments/sustainableDevelopment/developmentId"
    )

    sdg_id_lists = [
        get_sdg(development_id.text)
        for development_id in development_ids
        if development_id.text
    ]

    unique_sdgs = []
    for sdg_list in sdg_id_lists:
        for sdg in sdg_list:
            if sdg not in unique_sdgs:
                unique_sdgs.append(sdg)

    # Create topic elements for each unique SDG
    for i, sdg_id in enumerate(unique_sdgs):
        topic = ET.Element("topic", repeatId=str(i))
        topic.text = sdg_id
        subject.append(topic)

    return subject


def _create_topic(sdg_id: str, repeat_id: int) -> ET.Element:
    """
    Create a topic element for the SDG with the given ID and repeat ID.
    """
    topic = ET.Element("topic", repeatId=str(repeat_id))
    topic.text = sdg_id
    return topic
