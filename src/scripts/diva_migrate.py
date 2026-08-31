from common.arg_parser import create_argument_parser, classic_arguments
from cora.context import CoraContext
from cora_to_cora.organisations_migrate import organisations_migrate
from db_to_cora.publishers_migrate import publishers_migrate
from db_to_cora.funders_migrate import funders_migrate
from db_to_cora.journals_migrate import journals_migrate
from db_to_cora.subjects_migrate import subjects_migrate
from db_to_cora.programmes_migrate import programmes_migrate
from db_to_cora.courses_migrate import courses_migrate
from db_to_cora.series_migrate import series_migrate


def main():
    argparser = create_argument_parser(
        description="Migrate data from DiVA Classic to DiVA on Cora",
        arguments={
            "--domain": {
                "help": "Domain to migrate",
                "type": str,
                "required": True,
            },
            **classic_arguments,
            "--system": {
                "help": "Cora system to connect to (e.g., 'preview', 'production')",
                "type": str,
                "default": "minikube",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication.",
            },
            "--app-token": {
                "help": "Application token for authentication. If not provided, the script will look for an example user configured with this id",
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
            "--record-types": {
                "help": "Comma-separated list of record types to migrate. Available types: publishers, funders, journals, organisations, subjects, series, programmes, courses. If not specified, all types are migrated.",
                "type": str,
                "default": None,
            },
        },
    )
    args = argparser.parse_args()

    # Parse record types
    all_common_types = ["publishers", "funders", "journals"]
    all_domain_types = ["organisations", "subjects", "series", "programmes", "courses"]
    all_types = all_common_types + all_domain_types

    if args.record_types:
        selected_types = [t.strip() for t in args.record_types.split(",")]
        invalid_types = [t for t in selected_types if t not in all_types]
        if invalid_types:
            print(f"Error: Invalid record types: {invalid_types}")
            print(f"Available types: {all_types}")
            return
    else:
        selected_types = all_types

    print(
        r"""
 _______   __  __     __   ______         __       __  __                                 __       ______            
/       \ /  |/  |   /  | /      \       /  \     /  |/  |                               /  |     /      \           
$$$$$$$  |$$/ $$ |   $$ |/$$$$$$  |      $$  \   /$$ |$$/   ______    ______   ______   _$$ |_   /$$$$$$  |  ______  
$$ |  $$ |/  |$$ |   $$ |$$ |__$$ |      $$$  \ /$$$ |/  | /      \  /      \ /      \ / $$   |  $$$  \$$ | /      \ 
$$ |  $$ |$$ |$$  \ /$$/ $$    $$ |      $$$$  /$$$$ |$$ |/$$$$$$  |/$$$$$$  |$$$$$$  |$$$$$$/   $$$$  $$ |/$$$$$$  |
$$ |  $$ |$$ | $$  /$$/  $$$$$$$$ |      $$ $$ $$/$$ |$$ |$$ |  $$ |$$ |  $$/ /    $$ |  $$ | __ $$ $$ $$ |$$ |  $$/ 
$$ |__$$ |$$ |  $$ $$/   $$ |  $$ |      $$ |$$$/ $$ |$$ |$$ \__$$ |$$ |     /$$$$$$$ |  $$ |/  |$$ \$$$$ |$$ |      
$$    $$/ $$ |   $$$/    $$ |  $$ |      $$ | $/  $$ |$$ |$$    $$ |$$ |     $$    $$ |  $$  $$/ $$   $$$/ $$ |      
$$$$$$$/  $$/     $/     $$/   $$/       $$/      $$/ $$/  $$$$$$$ |$$/       $$$$$$$/    $$$$/   $$$$$$/  $$/       
                                                          /  \__$$ |                                                 
                                                          $$    $$/                                                  
                                                           $$$$$$/                                                   
                                                           
"""
    )

    context = CoraContext(
        args.system, args.login_id, args.app_token, workers=args.workers
    )
    context.log(f"=== Migration started for {args.domain} to {args.system} ===")

    # Determine which common types to migrate
    common_types_to_migrate = [t for t in all_common_types if t in selected_types]
    if args.include_common_data and common_types_to_migrate:
        print(f"=== Start migrating common data to {args.system} ===")
        print(f"    Record types: {common_types_to_migrate}")

        if "publishers" in selected_types:
            migrate_publishers(args, context)
        if "funders" in selected_types:
            migrate_funders(args, context)
        if "journals" in selected_types:
            migrate_journals(args, context)
        # TODO Persons
        # TODO Projects

        print("=== Common data migration completed ===")
    elif not args.include_common_data:
        print(
            "Skipping migrating common data, since --include-common-data arg is not set"
        )

    # Determine which domain types to migrate
    domain_types_to_migrate = [t for t in all_domain_types if t in selected_types]
    if domain_types_to_migrate:
        print(f"=== Start migrating data for {args.domain} domain to {args.system} ===")
        print(f"    Record types: {domain_types_to_migrate}")

        if "organisations" in selected_types:
            migrate_organisations(args, context)
        if "subjects" in selected_types:
            migrate_subjects(args, context)
        if "series" in selected_types:
            migrate_series(args, context)
        if "programmes" in selected_types:
            migrate_programmes(args, context)
        if "courses" in selected_types:
            migrate_courses(args, context)
        # TODO Outputs

        print(f"=== Data migration for {args.domain} domain completed ===")
    context.log(f"=== Migration completed for {args.domain} to {args.system} ===")


def migrate_publishers(args, context):
    print("--- Start migrating publishers")
    num_publishers = publishers_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password,
    )
    print(f"--- {num_publishers} Publishers imported to Cora ---")


def migrate_funders(args, context):
    print("--- Start migrating funders")
    num_funders = funders_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password,
    )
    print(f"--- {num_funders} Funders imported to Cora ---")


def migrate_journals(args, context):
    print("--- Start migrating journals ")
    num_journals = journals_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password,
    )
    print(f"--- {num_journals} Journals imported to Cora ---")


def migrate_organisations(args, context):
    print(f"--- Start migrating organisations for {args.domain} ---")
    num_organisations = organisations_migrate(context, args.domain)
    print(f"--- {num_organisations} Organisations migrated ---")


def migrate_subjects(args, context):
    print(f"--- Start migrating subjects for {args.domain} ---")
    num_subjects = subjects_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password, domain=args.domain,
    )
    print(f"--- {num_subjects} Subjects imported to Cora ---")


def migrate_programmes(args, context):
    print(f"--- Start migrating programmes for {args.domain} ---")
    num_programmes = programmes_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password, domain=args.domain,
    )
    print(f"--- {num_programmes} Programmes imported to Cora ---")


def migrate_courses(args, context):
    print(f"--- Start migrating courses for {args.domain} ---")
    num_courses = courses_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password, domain=args.domain,
    )
    print(f"--- {num_courses} Courses imported to Cora ---")


def migrate_series(args, context):
    print(f"--- Start migrating series for {args.domain} ---")
    num_series = series_migrate(
        context,
        db_host=args.db_host, db_port=args.db_port, db_name=args.db_name,
        db_user=args.db_user, db_password=args.db_password, domain=args.domain,
    )
    print(f"--- {num_series} Series imported to Cora ---")


if __name__ == "__main__":
    main()
