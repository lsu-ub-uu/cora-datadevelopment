from classic.get_subjects import get_subjects
from cora.context import Context
from db_to_cora.subject_programme_course_transform import transform_subject
from db_to_cora.records_import import records_import
from db_to_cora.update_relations import RelationMapping


def subjects_migrate(
    context: Context, db_user: str, db_password: str, domain: str
) -> int:
    """Migrate subjects from DiVA Classic to DiVA on Cora.

    Args:
        context: The Cora context for API operations.
        db_user: Database user for Classic Cora.
        db_password: Database password for Classic Cora.
        domain: Domain to migrate subjects for.

    Returns:
        The number of subjects migrated.
    """
    classic_subjects = get_subjects(
        db_user=db_user, db_password=db_password, domain=domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-subject",
        source_records=classic_subjects,
        transform_function=transform_subject,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="broader_id",
                new_relation_link="subject",
                new_relation_type="broader",
            ),
            RelationMapping(
                old_relation_tag="earlier_id",
                new_relation_link="subject",
                new_relation_type="earlier",
            ),
        ],
        apply=True,
    )

    return len(classic_subjects)
