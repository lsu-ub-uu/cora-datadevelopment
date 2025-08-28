from datetime import datetime
from common.run_rotating_logger import RunRotatingLogger
from common.threads import run_with_threads
from cora.context import Context
import xml.etree.ElementTree as ET
from fedora.get_pids_for_domain import get_pids_for_domain
from fedora.get_record_by_pid import get_record_by_pid
from common.xml_utils import save_to_file
from common.threads import run_with_threads


def import_publications_from_fedora(domain: str):
    time_started = _get_now()
    logger = RunRotatingLogger(
        "data", f"logs/import_publications_from_fedora.log"
    ).get()

    logger.info("==== Begin importing publications from Fedora ====")
    logger.info(f"==== domain={domain} ====")
    logger.info("==================================================")

    pids = get_pids_for_domain(domain)

    run_with_threads(
        pids,
        lambda pid: _import_publication(domain, pid, time_started),
    )
    logger.info(f"--- Successfully imported {len(pids)} publications to file ---")


def _import_publication(domain: str, pid: str, time_started: datetime) -> None:
    publication = get_record_by_pid(pid)
    save_to_file(
        publication,
        f"data/fedora_xml/{domain}/{time_started.isoformat()}/{pid}.xml",
    )
    # download_attachments(publication, domain)


if __name__ == "__main__":
    import_publications_from_fedora("uu")


def _get_now() -> datetime:
    return datetime.now()
