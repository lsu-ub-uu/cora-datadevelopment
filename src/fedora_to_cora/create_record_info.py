"""
Copyright 2025 Uppsala University Library

This file is part of DiVA Client.

    DiVA Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DiVA Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
"""

import xml.etree.ElementTree as ET
from common.common_data import create_record_link_using_name_type_id
from fedora_to_cora.get_validation_type_by_publication_type_id import get_validation_type_by_publication_type_id
from fedora_to_cora.get_visibility import get_visibility


def create_record_info(source_record):
    recordInfo = ET.Element("recordInfo")


    ET.SubElement(recordInfo, "validationType").text = get_validation_type_by_publication_type_id(
        source_record.find(".//publicationTypeId").text
    )

    ET.SubElement(recordInfo, "dataDivider").text = "divaData"

    recordInfo.append(create_record_link_using_name_type_id(
        "permissionUnit",
        "permissionUnit",
        source_record.find(".//domain").text
    ))

    ET.SubElement(recordInfo, "visibility").text = get_visibility(source_record)


    pid = source_record.find(".//pid")
    if pid is not None and pid.text:
        ET.SubElement(recordInfo, "oldId").text = pid.text

    return recordInfo