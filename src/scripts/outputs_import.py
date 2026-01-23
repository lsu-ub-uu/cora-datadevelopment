import argparse
from common.arg_parser import create_argument_parser
from common.ssh_tunnel import SSHTunnel
from cora.context import CoraContext
from fedora_to_cora.process_fedora_publication_files import (
    process_fedora_publication_files,
)
from scripts.util.analyze_errors import analyze_and_print_report
from classic.config import SSH_HOST, SSH_PORT, SSH_USER
import time
from multiprocessing import Pool
from fedora_to_cora.process_fedora_publication_files import _read_source_records, _validate_source_records
from fedora_to_cora.output_migrate import output_migrate
from tqdm import tqdm

context = None
with_binaries = False
apply = False

def init_context(system, login_id, app_token, apply_flag, binaries_flag):
    global context, apply, with_binaries
    context = CoraContext(system=system, login_id=login_id, app_token=app_token)
    apply = apply_flag
    with_binaries = binaries_flag

def worker(source_record):
    output_migrate(
        source_record, context, apply, with_binaries=with_binaries
    )

def main():
    """Main entry point for the outputs import script."""
    parser = create_argument_parser(
        description="Processes fedora XML publication files for a domain, transforms them to Cora format and imports them to the specified Cora system",
        arguments={
            "--xml-dir": {
                "help": "Directory containing XML files to process",
                "required": True,
            },
            "--system": {
                "default": "pre",
                "help": "Target system for migration",
            },
            "--login-id": {
                "default": "divaAdmin@cora.epc.ub.uu.se",
                "help": "Login ID for authentication",
            },
            "--app-token": {
                "help": "Application token for authentication",
            },
            "--workers": {
                "type": int,
                "default": 16,
                "help": "Number of worker threads",
            },
            "--apply": {
                "action": "store_true",
                "help": "Create records in Cora. (If not set, will behave as a dry-run)",
            },
            "--limit": {
                "type": int,
                "help": "Limit the number of processed files (for testing purposes)",
                "default": None,
            },
            "--binaries": {
                "action": "store_true",
                "help": "Also migrate binaries associated with the publications",
                "default": False,
            },
        },
    )

    args = parser.parse_args()

    # context = CoraContext(
    #     system=args.system,
    #     login_id=args.login_id,
    #     app_token=args.app_token,
    #     workers=args.workers,
    # )

    REMOTE_HOST = "10.0.2.68"
    REMOTE_PORT = 8088
    LOCAL_PORT = 8088

    print(
        """
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

    start_time = time.perf_counter()

    # with SSHTunnel(SSH_HOST, SSH_PORT, SSH_USER, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT):
    #     process_fedora_publication_files(
    #         xml_dir=args.xml_dir,
    #         context=context,
    #         apply=args.apply,
    #         limit=args.limit,
    #         binaries=args.binaries,
    #     )


   

    # ...parse args...
    source_records = _read_source_records(args.xml_dir, args.limit)
    source_records_valid = _validate_source_records(source_records)
    
    if not source_records_valid:
        print("Source records validation failed. Exiting.")
        return
    
    with Pool(4, initializer=init_context, initargs=(args.system, args.login_id, args.app_token, args.apply, args.binaries)) as pool:
        #pool.imap_unordered(worker, source_records),
        list(
            tqdm(
                pool.imap_unordered(worker, source_records),
                total=len(source_records),
                desc="Processing source records",
            )
        )
            


    end_time = time.perf_counter()
    print(f"Processing completed in {end_time - start_time:.2f} seconds.")

    analyze_and_print_report("logs/outputs-import.log")


if __name__ == "__main__":
    main()
