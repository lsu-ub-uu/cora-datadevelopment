from typing import Tuple
import requests
from cora.validate import validate_record
from cora.create import create_record, is_success_result
from cora.update import update_record
from cora_to_cora.transform_organisation import transform_organisation
from cora_to_cora.update_organisation_relations import update_organisation_relations
import xml.etree.ElementTree as ET


def organisations_migrate(context, domain, apply):
    search_result = _get_old_cora_organisations(context, domain)
    number_of_results = int(search_result["dataList"]["totalNo"])
    if number_of_results == 0:
        context.log("No organisations found to migrate from old Cora system.")
        return
    context.log(
        f"Found {number_of_results} organisations to migrate from old Cora system."
    )
    old_organisations = search_result["dataList"]["data"]

    if apply:
        organisation_migration_pairs: list[Tuple[dict, ET.Element]] = []
        for old_org in old_organisations:
            new_org = transform_organisation(old_org, context)
            created_org = create_record(new_org, context)
            if not is_success_result(created_org):
                context.log(
                    f"Failed to create organisation for old ID {old_org.get('id')}: {created_org.error}"
                )
                raise Exception("Aborting migration due to create record failure.")
            organisation_migration_pairs.append((old_org, created_org.response_data))
        update_organisation_relations(organisation_migration_pairs)
    else:
        for org in old_organisations:
            new_org = transform_organisation(org, context)
            validate_record(new_org, record_type="diva-organisation", context=context)


def _get_old_cora_organisations(context, domain):
    try:
        response = requests.get(
            f'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={{"name":"search","children":[{{"name":"include","children":[{{"name":"includePart","children":[{{"name":"divaOrganisationDomainSearchTerm","value":"{domain}"}}]}}]}}]}}'
        )
        return response.json()
    except Exception as e:
        raise Exception(
            f"Failed to fetch organisations from old Cora: {response.status_code} {response.text}"
        ) from e
