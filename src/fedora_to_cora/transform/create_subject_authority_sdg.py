import xml.etree.ElementTree as ET
from common.xml_utils import create_group
from fedora_to_cora.transform.get_sdg import get_sdg
from common.xml_utils import create_group, create_text


def create_subject_authority_sdg(source_record: ET.Element) -> ET.Element | None:
    """
    Create a subject element with authority "sdg" based on the source record.
    """

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

    return create_group(
        "subject",
        authority="sdg",
        children=[
            create_text("topic", repeatId=str(i), value=sdg_id)
            for i, sdg_id in enumerate(unique_sdgs)
        ],
    )
