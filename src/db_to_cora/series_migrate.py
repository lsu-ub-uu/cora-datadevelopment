from classic.get_series import get_series
from cora.context import Context
from db_to_cora.series_transform import transform_series
from db_to_cora.records_import import records_import
from db_to_cora.update_relations import RelationMapping


def series_migrate(
    context: Context, db_user: str, db_password: str, domain: str
) -> int:
    """Migrate series from DiVA Classic to DiVA on Cora.

    Args:
        context: The Cora context for API operations.
        db_user: Database user for Classic Cora.
        db_password: Database password for Classic Cora.
        domain: Domain to migrate series for.

    Returns:
        The number of series migrated.
    """
    classic_series = get_series(
        db_user=db_user, db_password=db_password, domain=domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-series",
        source_records=classic_series,
        transform_function=transform_series,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="relative_id_host",
                new_relation_link="topic",
                new_relation_type="host",
            ),
            RelationMapping(
                old_relation_tag="relative_id_preceding",
                new_relation_link="topic",
                new_relation_type="preceding",
            ),
        ],
        apply=True,
    )

    return len(classic_series)
