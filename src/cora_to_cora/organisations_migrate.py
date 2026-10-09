from typing import Tuple
import json
import logging
import requests
from common.threads import run_with_threads
from cora.create import create_record, is_success_result
from cora_to_cora.transform_organisation import transform_organisation
from cora_to_cora.update_organisation_relations import update_organisation_relations
from cora.cora_json_utils import (
    find_child_with_name_in_data,
    get_first_atomic_value_with_name_in_data,
    get_linked_record_id_with_name_in_data,
)
import xml.etree.ElementTree as ET
from cora.context import Context, CoraContext

logger = logging.getLogger(__name__)

VALID_ORGANISATION_DOMAINS = frozenset(
    {
        "hh",
        "miun",
        "hig",
        "naturvardsverket",
        "kkh",
        "hv",
        "fmv",
        "du",
        "skh",
        "mchs",
        "his",
        "raa",
        "nai",
        "liu",
        "norden",
        "kth",
        "uu",
        "riksarkivet",
        "nrm",
        "isof",
        "ehs",
        "lnu",
        "shh",
        "konstfack",
        "cora",
        "havochvatten",
        "ri",
        "trafikverket",
        "mdu",
        "gih",
        "kmh",
        "ju",
        "rkh",
        "nationalmuseum",
        "sh",
        "swedgeo",
        "bth",
        "umu",
        "kau",
        "ivl",
        "diva",
        "mau",
        "polar",
        "su",
        "vti",
        "ltu",
        "smhi",
        "fhs",
        "nordiskamuseet",
        "oru",
        "hb",
    }
)


def organisations_migrate(context: Context, domain: str | None = None):
    old_organisations = _get_old_cora_organisations(context, domain)

    if len(old_organisations) == 0:
        logger.info("No organisations found to migrate from old Cora system.")
        return

    logger.info(
        f"Found {len(old_organisations)} organisations to migrate from old Cora system."
    )

    organisation_migration_pairs: list[Tuple[dict, ET.Element]] = []

    def transform_and_create_organisation(old_org: dict):
        new_org = transform_organisation(old_org)
        created_org = create_record(
            new_org, record_type="diva-organisation", context=context
        )
        if not is_success_result(created_org):
            if created_org.error and "status 409" in created_org.error:
                logger.info(
                    f"Skipping organisation with old ID {new_org.findtext('./recordInfo/oldId')}: already exists in the system."
                )
                return
            logger.info(
                f"Failed to create organisation for old ID {new_org.findtext('./recordInfo/oldId')}: {created_org.error}"
            )
            raise Exception(
                f"Aborting migration due to create record failure for old ID {new_org.findtext('./recordInfo/oldId')}: {created_org.error}"
            )
        organisation_migration_pairs.append((old_org, created_org.response_data))

    run_with_threads(
        old_organisations,
        transform_and_create_organisation,
        workers=context.get_workers(),
        desc="Transforming and creating organisations",
    )

    update_organisation_relations(organisation_migration_pairs, context)
    return len(organisation_migration_pairs)


def _get_old_cora_organisations(context, domain: str | None = None):
    search_term = {"name": "organisationGeneralSearchTerm", "value": "*"}
    if domain is not None:
        search_term = {"name": "divaOrganisationDomainSearchTerm", "value": domain}
    children = [
        {
            "name": "include",
            "children": [{"name": "includePart", "children": [search_term]}],
        }
    ]
    page_size = 1000
    start = {"name": "start", "value": "1"}
    children.extend([{"name": "rows", "value": str(page_size)}, start])
    search_data = {"name": "search", "children": children}
    organisations = []
    total = 1
    offset = 1
    while offset <= total:
        start["value"] = str(offset)
        response = requests.get(
            "https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch",
            params={"searchData": json.dumps(search_data)},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch organisations from old Cora: {response.status_code} {response.text}"
            )
        data_list = response.json()["dataList"]
        if offset == 1:
            total = int(data_list["totalNo"])
        page = data_list["data"]
        if not page and offset <= total:
            raise Exception(f"Empty organisation page at start {offset}")
        organisations.extend(page)
        offset += page_size
    return list(filter(_should_migrate_organisation, organisations))


def _should_migrate_organisation(old_org: dict) -> bool:
    old_org_data = old_org["record"]["data"]

    record_info = find_child_with_name_in_data(old_org_data["children"], "recordInfo")
    assert record_info is not None
    record_type_id = get_linked_record_id_with_name_in_data(
        record_info["children"], "type"
    )
    domain = get_first_atomic_value_with_name_in_data(record_info["children"], "domain")
    return record_type_id != "rootOrganisation" and domain in VALID_ORGANISATION_DOMAINS
