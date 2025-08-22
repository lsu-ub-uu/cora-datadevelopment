import xml.etree.ElementTree as ET

file_label_id_to_type = {
    "50": "fullText",
    "51": "errata",
    "52": "references",
    "53": "summary",
    "54": "inside",
    "55": "cover",
    "56": "toc",
    "57": "popularSummary",
    "58": "audio",
    "59": "movie",
    "60": "imageDiva",
    "61": "attachment",
    "62": "notificationOfSubmissionOfAThesis",
    "63": "software",
    "64": "previewImage",
    "65": "dataSet",
}


def get_attachment_type(source_attachment: ET.Element) -> str:
    file_label_id = source_attachment.findtext("./fileLabel/fileLabelId")

    if file_label_id is None:
        raise ValueError("fileLabelId not found in attachment")

    attachment_type = file_label_id_to_type.get(file_label_id)

    if attachment_type is None:
        raise ValueError(f"Unknown fileLabelId: {file_label_id}")

    return attachment_type
