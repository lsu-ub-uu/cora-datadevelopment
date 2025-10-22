from typing import Tuple
import requests
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from cora.update import update_record
from cora_to_cora.transform_organisation import transform_organisation
from cora_to_cora.update_organisation_relations import update_organisation_relations
from cora.cora_json_utils import (
    find_child_with_name_in_data,
    get_linked_record_id_with_name_in_data,
)
import xml.etree.ElementTree as ET


def organisations_migrate(context, domain, apply):
    old_organisations = _get_old_cora_organisations(context, domain)

    if len(old_organisations) == 0:
        context.log("No organisations found to migrate from old Cora system.")
        return

    context.log(
        f"Found {len(old_organisations)} organisations to migrate from old Cora system."
    )
    if apply:
        organisation_migration_pairs: list[Tuple[dict, ET.Element]] = []
        for old_org in old_organisations:
            new_org = transform_organisation(old_org, context)
            created_org = create_record(
                new_org, record_type="diva-organisation", context=context
            )
            if not is_success_result(created_org):
                context.log(
                    f"Failed to create organisation for old ID {old_org.get('id')}: {created_org.error}"
                )
                raise Exception("Aborting migration due to create record failure.")
            organisation_migration_pairs.append((old_org, created_org.response_data))
        update_organisation_relations(organisation_migration_pairs, context)
    else:
        for org in old_organisations:
            new_org = transform_organisation(org, context)
            validate_record(new_org, record_type="diva-organisation", context=context)


def _get_old_cora_organisations(context, domain):
    response = requests.get(
        f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}}]}}'
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch organisations from old Cora: {response.status_code} {response.text}"
        )
    search_result = response.json()
    return list(filter(_is_not_root_organisation, search_result["dataList"]["data"]))


def _is_not_root_organisation(old_org: dict) -> bool:
    old_org_data = old_org["record"]["data"]

    record_info = find_child_with_name_in_data(old_org_data["children"], "recordInfo")
    assert record_info is not None
    record_type_id = get_linked_record_id_with_name_in_data(
        record_info["children"], "type"
    )
    return record_type_id != "rootOrganisation"
