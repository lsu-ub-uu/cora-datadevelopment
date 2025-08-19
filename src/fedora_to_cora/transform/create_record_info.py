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
from fedora_to_cora.transform.get_validation_type_by_publication_type_id import (
    get_validation_type_from_fedora_record,
)
from fedora_to_cora.transform.get_visibility import get_visibility
from common.record_info_create import record_info_create


def create_record_info(source_record: ET.Element) -> ET.Element:
    validation_type = get_validation_type_from_fedora_record(source_record)

    permission_unit = _create_permission_unit(source_record)

    visibility = get_visibility(source_record)

    old_id = _create_old_id(source_record)

    return record_info_create(
        validation_type_id=validation_type,
        old_id=old_id,
        permission_unit_id=permission_unit,
        visibility=visibility,
    )


def _create_permission_unit(source_record: ET.Element) -> str:
    domain = source_record.find("./administrativeInfo/domain")
    assert (
        domain is not None and domain.text is not None
    ), "domain is missing in source record"

    return domain.text


def _create_old_id(source_record: ET.Element) -> str:
    pid = source_record.find("./pid")
    assert pid is not None and pid.text is not None, "pid is missing in source record"

    return pid.text
