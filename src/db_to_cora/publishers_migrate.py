from classic.get_publishers import get_publishers
from cora.context import Context
from db_to_cora.publisher_transform import transform_publisher
from db_to_cora.records_import import records_import


def publishers_migrate(context: Context, db_user: str, db_password: str) -> int:
    """Migrate publishers from DiVA Classic to DiVA on Cora.

    Args:
        context: The Cora context for API operations.
        db_user: Database user for Classic Cora.
        db_password: Database password for Classic Cora.

    Returns:
        The number of publishers migrated.
    """
    classic_publishers = get_publishers(
        db_user=db_user, db_password=db_password
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-publisher",
        source_records=classic_publishers,
        transform_function=transform_publisher,
        apply=True,
    )

    return len(classic_publishers)
