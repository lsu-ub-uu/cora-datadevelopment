from datetime import datetime
from common.run_rotating_logger import RunRotatingLogger
from common.threads import run_with_threads
from cora.context import Context
import xml.etree.ElementTree as ET
from classic.get_pids_for_domain import get_pids_for_domain
from classic.get_record_by_pid import get_record_by_pid
from common.xml_utils import save_to_file
from common.threads import run_with_threads


def export_publications_from_fedora(domain: str, workers=16):
    time_started = _get_now()
    dirname = f"data/fedora_xml/{domain}/{time_started.isoformat()}"
    logger = RunRotatingLogger(
        "data", f"logs/import_publications_from_fedora.log"
    ).get()

    logger.info("==== Begin importing publications from Fedora ====")
    logger.info(f"==== domain={domain} ====")
    logger.info("==================================================")

    pids = get_pids_for_domain(domain)
    logger.info(f"Found {len(pids)} publications in domain {domain}")

    def import_publication(pid: str) -> None:
        try:
            publication = get_record_by_pid(pid)
            save_to_file(
                publication,
                f"{dirname}/{pid}.xml",
            )
            logger.info(f"Successfully imported publication {pid}")
            # download_attachments(publication, domain)
        except Exception as e:
            logger.error(f"Failed to import publication {pid}: {e}")

    run_with_threads(
        pids,
        import_publication,
        workers=workers,
        desc="Importing publications from Fedora",
    )

    logger.info(f"--- Successfully imported {len(pids)} publications to {dirname} ---")
    print(f"--- Successfully imported {len(pids)} publications to {dirname} ---")


def _get_now() -> datetime:
    return datetime.now()
