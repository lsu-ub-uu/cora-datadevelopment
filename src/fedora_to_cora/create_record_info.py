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
from fedora_to_cora.get_validation_type_by_publication_type_id import (
    get_validation_type_by_publication_type_id,
)
from fedora_to_cora.get_visibility import get_visibility


def create_record_info(source_record: ET.Element) -> ET.Element:
    recordInfo = ET.Element("recordInfo")

    recordInfo.append(_create_validation_type(source_record))

    recordInfo.append(_create_data_divider())

    recordInfo.append(_create_permission_unit(source_record))

    ET.SubElement(recordInfo, "visibility").text = get_visibility(source_record)

    recordInfo.append(_create_old_id(source_record))

    return recordInfo


def _create_validation_type(source_record: ET.Element) -> ET.Element:
    publicationTypeId = source_record.find(".//publicationTypeId")
    assert (
        publicationTypeId is not None and publicationTypeId.text is not None
    ), "publicationTypeId is missing in source record"

    return create_record_link_using_name_type_id(
        "validationType",
        record_type="validationType",
        record_id=get_validation_type_by_publication_type_id(publicationTypeId.text),
    )


def _create_data_divider() -> ET.Element:
    return create_record_link_using_name_type_id(
        "dataDivider",
        record_type="system",
        record_id="divaData",
    )


def _create_permission_unit(source_record: ET.Element) -> ET.Element:
    domain = source_record.find(".//domain")
    assert (
        domain is not None and domain.text is not None
    ), "domain is missing in source record"

    return create_record_link_using_name_type_id(
        "permissionUnit",
        record_type="permissionUnit",
        record_id=domain.text,
    )


def _create_old_id(source_record: ET.Element) -> ET.Element:
    pid = source_record.find(".//pid")
    assert pid is not None and pid.text is not None, "pid is missing in source record"

    oldId = ET.Element("oldId")
    oldId.text = pid.text
    return oldId
