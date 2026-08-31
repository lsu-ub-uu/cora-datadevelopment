from classic.get_funders import get_funders
from cora.context import Context
from db_to_cora.funder_transform import transform_funder
from db_to_cora.records_import import records_import


def funders_migrate(
    context: Context,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
) -> int:
    classic_funders = get_funders(
        db_host=db_host, db_port=db_port, db_name=db_name,
        db_user=db_user, db_password=db_password,
    ).findall(
        ".//DATA_RECORD"
    )

    records_import(
        context,
        record_type="diva-funder",
        source_records=classic_funders,
        transform_function=transform_funder,
        apply=True,
    )

    return len(classic_funders)
