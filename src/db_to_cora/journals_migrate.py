from classic.get_journals import get_journals
from cora.context import Context
from db_to_cora.journal_transform import transform_journal
from db_to_cora.records_import import records_import


def journals_migrate(context: Context, db_user: str, db_password: str) -> int:
    """Migrate journals from DiVA Classic to DiVA on Cora.

    Args:
        context: The Cora context for API operations.
        db_user: Database user for Classic Cora.
        db_password: Database password for Classic Cora.

    Returns:
        The number of journals migrated.
    """
    classic_journals = get_journals(db_user=db_user, db_password=db_password).findall(
        ".//DATA_RECORD"
    )

    records_import(
        context,
        record_type="diva-journal",
        source_records=classic_journals,
        transform_function=transform_journal,
        apply=True,
    )

    return len(classic_journals)
