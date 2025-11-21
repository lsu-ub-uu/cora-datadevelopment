from common.arg_parser import create_argument_parser
from classic.get_publishers import get_publishers
from classic.get_funders import get_funders
from cora.context import Context, CoraContext
from db_to_cora.funder_transform import transform_funder
from db_to_cora.journal_transform import transform_journal
from db_to_cora.publisher_transform import transform_publisher
from classic.get_journals import get_journals
from cora_to_cora.organisations_migrate import organisations_migrate
from db_to_cora.series_transform import transform_series
from db_to_cora.subject_programme_course_transform import (
    transform_subject,
    transform_programme,
    transform_course,
)
from classic.get_subjects import get_subjects
from classic.get_programmes import get_programmes
from classic.get_courses import get_courses
from classic.get_series import get_series
from db_to_cora.records_import import records_import
from db_to_cora.update_relations import RelationMapping, update_relations


def main():
    argparser = create_argument_parser(
        description="Migrate data from DiVA Classic to DiVA on Cora",
        arguments={
            "--domain": {
                "help": "Domain to migrate",
                "type": str,
                "required": True,
            },
            "--db-user": {
                "help": "Database user for Classic Cora",
                "type": str,
                "required": True,
            },
            "--db-password": {
                "help": "Database password for Classic Cora",
                "type": str,
                "required": True,
            },
            "--system": {
                "help": "Cora system to connect to (e.g., 'preview', 'production')",
                "type": str,
                "default": "minikube",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "default": "49ce00fb-68b5-4089-a5f7-1c225d3cf156",
                "help": "Application token for authentication",
            },
            "--workers": {
                "help": "Number of worker threads for processing",
                "type": int,
                "default": 16,
            },
            "--include-common-data": {
                "help": "Include common data (publishers, funders, journals) in the migration",
                "action": "store_true",
            },
        },
    )
    args = argparser.parse_args()

    context = CoraContext(
        args.system, args.login_id, args.app_token, workers=args.workers
    )
    context.log(f"=== Migration started for {args.domain} to {args.system} ===")
    if args.include_common_data:
        print(f"=== Start migrating common data to {args.system} ===")

        migrate_publishers(args, context)
        migrate_funders(args, context)
        # migrate_journals(args, context)
        # TODO Persons
        # TODO Projects

        print("=== Common data migration completed ===")
    else:
        print(
            "Skipping migrating common data, since --include-common-data arg is not set"
        )

    print(f"=== Start migrating data for {args.domain} domain to {args.system} ===")

    migrate_organisations(args, context)
    migrate_subjects(args, context)
    migrate_series(args, context)
    migrate_programmes(args, context)
    migrate_course(args, context)
    # TODO Outputs

    print(f"=== Data migration for {args.domain} domain completed ===")
    context.log(f"=== Migration completed for {args.domain} to {args.system} ===")


def migrate_publishers(args, context: Context):
    print("--- Start migrating publishers")
    classic_publishers = get_publishers(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-publisher",
        source_records=classic_publishers,
        transform_function=transform_publisher,
        apply=True,
    )
    print(f"--- {len(classic_publishers)} Publishers imported to Cora ---")


def migrate_funders(args, context: Context):
    print("--- Start migrating funders")
    classic_funders = get_funders(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-funder",
        source_records=classic_funders,
        transform_function=transform_funder,
        apply=True,
    )

    print(f"--- {len(classic_funders)} Funders imported to Cora ---")


def migrate_journals(args, context: Context):
    print("--- Start migrating journals ")
    classic_journals = get_journals(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-journal",
        source_records=classic_journals,
        transform_function=transform_journal,
        apply=True,
    )
    print(f"--- {len(classic_journals)} Journals imported to Cora ---")


def migrate_organisations(args, context: Context):
    print(f"--- Start migrating organisations for {args.domain} ---")
    num_organisations = organisations_migrate(context, args.domain)
    print(f"--- {num_organisations} Organisations migrated ---")


def migrate_subjects(args, context: Context):
    print(f"--- Start migrating subjects for {args.domain} ---")
    classic_subjects = get_subjects(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-subject",
        source_records=classic_subjects,
        transform_function=transform_subject,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="broader_id",
                new_relation_link="topic",
                new_relation_type="broader",
            ),
            RelationMapping(
                old_relation_tag="earlier_id",
                new_relation_link="topic",
                new_relation_type="earlier",
            ),
        ],
        apply=True,
    )

    print(f"--- {len(classic_subjects)} Subjects imported to Cora ---")


def migrate_programmes(args, context: Context):
    print(f"--- Start migrating programmes for {args.domain} ---")
    classic_programmes = get_programmes(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-programme",
        source_records=classic_programmes,
        transform_function=transform_programme,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="broader_id",
                new_relation_link="programme",
                new_relation_type="broader",
            ),
            RelationMapping(
                old_relation_tag="earlier_id",
                new_relation_link="programme",
                new_relation_type="earlier",
            ),
        ],
        apply=True,
    )
    print(f"--- {len(classic_programmes)} Programmes imported to Cora ---")


def migrate_course(args, context: Context):
    print(f"--- Start migrating courses for {args.domain} ---")
    classic_courses = get_courses(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-course",
        source_records=classic_courses,
        transform_function=transform_course,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="broader_id",
                new_relation_link="course",
                new_relation_type="broader",
            ),
            RelationMapping(
                old_relation_tag="earlier_id",
                new_relation_link="course",
                new_relation_type="earlier",
            ),
        ],
        apply=True,
    )
    print(f"--- {len(classic_courses)} Courses imported to Cora ---")


def migrate_series(args, context: Context):
    print(f"--- Start migrating series for {args.domain} ---")
    classic_series = get_series(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")

    records_import(
        context,
        record_type="diva-series",
        source_records=classic_series,
        transform_function=transform_series,
        relation_mappings=[
            RelationMapping(
                old_relation_tag="relative_id_host",
                new_relation_link="series",
                new_relation_type="host",
            ),
            RelationMapping(
                old_relation_tag="relative_id_preceding",
                new_relation_link="series",
                new_relation_type="preceding",
            ),
        ],
        apply=True,
    )
    print(f"--- {len(classic_series)} Series imported to Cora ---")


if __name__ == "__main__":
    main()
