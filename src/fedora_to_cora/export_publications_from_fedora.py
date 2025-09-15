from datetime import datetime
from common.run_rotating_logger import RunRotatingLogger
from common.ssh_tunnel import diva_ssh_connection
import xml.etree.ElementTree as ET
from classic.get_pids_for_domain import get_pids_for_domain
from classic.get_publications_from_fedora import get_publications_from_fedora
from common.xml_utils import save_to_file


def export_publications_from_fedora(domain: str, workers=16):
    time_started = _get_now()
    dirname = f"data/fedora_xml/{domain}/{time_started.isoformat()}"

    logger = RunRotatingLogger(
        "data", f"logs/export_publications_from_fedora.log"
    ).get()

    logger.info("==== Begin exporting publications from Fedora ====")
    logger.info(f"==== domain={domain} ====")
    logger.info("==================================================")

    with diva_ssh_connection() as ssh_connection:
        pids = get_pids_for_domain(ssh_connection, domain)
        logger.info(f"Found {len(pids)} publications in domain {domain}")

        get_publications_from_fedora(
            ssh_connection, pids, workers=workers, dirname=dirname
        )

    logger.info(f"--- Successfully exported {len(pids)} publications to {dirname} ---")
    print(f"--- Successfully exported {len(pids)} publications to {dirname} ---")


def _get_now() -> datetime:
    return datetime.now()
