from common.arg_parser import create_argument_parser
from classic.get_publishers import get_publishers
from classic.get_funders import get_funders
from common.xml_utils import transform_record_list
from cora import context
from cora.context import Context, CoraContext
from cora.validate import validate_record_list
from cora.create import create_record_list
from db_to_cora.funder_transform import transform_funder
from db_to_cora.journal_transform import transform_journal
from db_to_cora.publisher_transform import transform_publisher
from classic.get_journals import get_journals
from cora_to_cora.organisations_migrate import organisations_migrate
from db_to_cora.series_transform import transform_series
from db_to_cora.subject_transform import transform_subject
from classic.get_subjects import get_subjects
from classic.get_series import get_series


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

    if args.include_common_data:
        print(f"=== Start migrating common data to {args.system} ===")

        _migrate_publishers(args, context)
        _migrate_funders(args, context)
        # _migrate_journals(args, context)
        # TODO Persons
        # TODO Projects

        print("=== Common data migration completed ===")
    else:
        print(
            "Skipping migrating common data, since --include-common-data arg is not set"
        )

    print(f"=== Start migrating data for {args.domain} domain to {args.system} ===")

    _migrate_organisations(args, context)
    _migrate_subjects(args, context)
    _migrate_series(args, context)
    # TODO Courses
    # TODO Programmes
    # TODO Outputs

    print(f"=== Data migration for {args.domain} domain completed ===")


def _migrate_publishers(args, context: Context):
    print("--- Start migrating publishers")
    classic_publishers = get_publishers(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")

    cora_publishers = transform_record_list(
        classic_publishers, transform_publisher, context
    )
    create_record_list(cora_publishers, "diva-publisher", context)
    print(f"--- {len(cora_publishers)} Publishers imported to Cora ---")


def _migrate_funders(args, context: Context):
    print("--- Start migrating funders")
    classic_funders = get_funders(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")
    cora_funders = transform_record_list(classic_funders, transform_funder, context)
    create_record_list(cora_funders, "diva-funder", context)
    print(f"--- {len(cora_funders)} Funders imported to Cora ---")


def _migrate_journals(args, context: Context):
    print("--- Start migrating journals ")
    classic_journals = get_journals(
        db_user=args.db_user, db_password=args.db_password
    ).findall(".//DATA_RECORD")
    cora_journals = transform_record_list(classic_journals, transform_journal, context)
    create_record_list(cora_journals, "diva-journal", context)
    print(f"--- {len(cora_journals)} Journals imported to Cora ---")


def _migrate_organisations(args, context: Context):
    print(f"--- Start migrating organisations for {args.domain} ---")
    num_organisations = organisations_migrate(context, args.domain)
    print(f"--- {num_organisations} Organisations migrated ---")


def _migrate_subjects(args, context: Context):
    print(f"--- Start migrating subjects for {args.domain} ---")
    classic_subjects = get_subjects(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")
    cora_subjects = transform_record_list(classic_subjects, transform_subject, context)
    create_record_list(cora_subjects, "diva-subject", context)
    print(f"--- {len(cora_subjects)} Subjects imported to Cora ---")


def _migrate_series(args, context: Context):
    print(f"--- Start migrating series for {args.domain} ---")
    classic_series = get_series(
        db_user=args.db_user, db_password=args.db_password, domain=args.domain
    ).findall(".//DATA_RECORD")
    cora_series = transform_record_list(classic_series, transform_series, context)
    create_record_list(cora_series, "diva-series", context)
    print(f"--- {len(cora_series)} Series imported to Cora ---")


if __name__ == "__main__":
    main()
