# CORA-3879

This series of scripts takes a dump of all authority person xmls to disk, then runs statistical analysis on that data.

- 01_export_authority_person_pids.py: Finds all authority-person pids from authority-archive and writes them to a JSON file
- 02_export_authority_person_xmls.py: Goes through the list of pids from the previous step, fetches the XML representation from authority-archive and dumps them to files.
- 03_analyze_authority_person_event_statistics.py: Analyzes the data to find the number of create and update events per month