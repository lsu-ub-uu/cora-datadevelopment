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
from fedora_to_cora.transform.get_validation_type import (
    get_validation_type_from_fedora_record,
)
from fedora_to_cora.transform.get_visibility import get_visibility
from common.record_info_create import record_info_create
from common.common_data import create_record_link
from cora.context import Context
from cora.get_cora_id_by_old_id import get_cora_id_by_old_id


def create_record_info(source_record: ET.Element, context: Context) -> ET.Element:
    validation_type = get_validation_type_from_fedora_record(source_record)
    assert (
        validation_type is not None
    ), "validation type could not be determined from source record"

    permission_unit = _create_permission_unit(source_record)

    visibility = get_visibility(source_record)

    old_id = _create_old_id(source_record)

    record_info = record_info_create(
        validation_type_id=validation_type,
        old_id=old_id,
        permission_unit_id=permission_unit,
        visibility=visibility,
        urn=source_record.findtext("./nbn"),
    )
    old_record_link = create_record_link(
        "oldRecord",
        "diva-oldRecord",
        get_cora_id_by_old_id(old_id, record_type="diva-oldRecord", context=context),
    )
    assert old_record_link is not None
    record_info.append(old_record_link)
    return record_info


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
