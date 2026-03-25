from classic.get_funders import get_funders
from cora.context import Context
from db_to_cora.funder_transform import transform_funder
from db_to_cora.records_import import records_import


def funders_migrate(context: Context, db_user: str, db_password: str) -> int:
    """Migrate funders from DiVA Classic to DiVA on Cora.

    Args:
        context: The Cora context for API operations.
        db_user: Database user for Classic Cora.
        db_password: Database password for Classic Cora.

    Returns:
        The number of funders migrated.
    """
    classic_funders = get_funders(db_user=db_user, db_password=db_password).findall(
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
