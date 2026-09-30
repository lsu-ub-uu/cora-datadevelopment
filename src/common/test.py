import os
import re
from pathlib import Path

SITE_CONFIG_ROOT = "/etc/apache2/sites-available"
PROMETHEUS_OUTPUT = Path("/tmp/prometheus/anubis_config.prom")


def proxy_regex(directive: str, page: str) -> tuple[str, re.Pattern]:
    label = f"{directive} /smash/{page}"
    pattern = re.compile(
        rf"^{directive} /smash/{re.escape(page)} "
        rf"http://diva2-search-.+:\$\{{.+-anubis-port\}}/smash/{re.escape(page)}$"
    )
    return label, pattern


REGEXES = [
    proxy_regex("ProxyPass", "resultList.jsf"),
    proxy_regex("ProxyPassReverse", "resultList.jsf"),
    proxy_regex("ProxyPass", "record.jsf"),
    proxy_regex("ProxyPassReverse", "record.jsf"),
]


def find_missing_directives(lines) -> list[str]:
    """Return labels of directives that were not found in the given lines."""
    stripped = [line.strip() for line in lines]
    missing = []
    for label, pattern in REGEXES:
        if not any(pattern.search(line) for line in stripped):
            missing.append(label)
    return missing


def write_prometheus_metrics(misconfigured: dict[str, list[str]]):
    """Write metrics to Prometheus text format file."""
    PROMETHEUS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    total_sites = misconfigured.get("_total", 0)
    fully_configured = misconfigured.get("_configured", 0)

    with open(PROMETHEUS_OUTPUT, "w", encoding="UTF-8") as f:
        f.write("# HELP anubis_sites_total Total Apache sites with -https suffix\n")
        f.write("# TYPE anubis_sites_total gauge\n")
        f.write(f"anubis_sites_total {total_sites}\n\n")

        f.write(
            "# HELP anubis_sites_configured Sites with all Anubis directives configured\n"
        )
        f.write("# TYPE anubis_sites_configured gauge\n")
        f.write(f"anubis_sites_configured {fully_configured}\n\n")

        f.write(
            "# HELP anubis_sites_misconfigured Sites missing at least one Anubis directive\n"
        )
        f.write("# TYPE anubis_sites_misconfigured gauge\n")
        f.write(f"anubis_sites_misconfigured {len(misconfigured) - 2}\n\n")

        if misconfigured.get("sites"):
            f.write(
                "# HELP anubis_site_missing_directives Number of missing directives per site\n"
            )
            f.write("# TYPE anubis_site_missing_directives gauge\n")
            for site_name, missing_list in misconfigured.get("sites", {}).items():
                f.write(
                    f'anubis_site_missing_directives{{site="{site_name}"}} {len(missing_list)}\n'
                )


def main():
    misconfigured = {"_total": 0, "_configured": 0, "sites": {}}

    for file_name in sorted(os.listdir(SITE_CONFIG_ROOT)):
        file_path = os.path.join(SITE_CONFIG_ROOT, file_name)
        if not os.path.isfile(file_path) or not file_name.endswith("-https"):
            continue

        misconfigured["_total"] += 1

        with open(file_path, encoding="UTF-8") as file:
            missing = find_missing_directives(file)

        if missing:
            misconfigured["sites"][file_name] = missing
        else:
            misconfigured["_configured"] += 1

    # Print misconfigured sites
    if misconfigured["sites"]:
        print("\nAnubis is NOT configured for the following sites:")
        for file_name, missing in misconfigured["sites"].items():
            print(f"\n  {file_name}")
            for label in missing:
                print(f"    - missing: {label}")

    # Write Prometheus metrics
    write_prometheus_metrics(misconfigured)
    print(f"\nMetrics written to {PROMETHEUS_OUTPUT}")


if __name__ == "__main__":
    main()
