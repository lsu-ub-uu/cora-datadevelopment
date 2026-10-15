## CORA-3756

This script restores attachments for a fixed list of classic quality `diva-output` records whose binaries are missing. For each record, it reads the corresponding source XML file and migrates its attachments into the Cora record.

The record IDs are defined in the script. Set `--xml-path` to the directory containing the source XML files and `--fedora-url` to the Classic Fedora service URL. The script updates the selected Cora system directly.

```shell
python src/scripts/one_off/CORA_3756_fix_classic_quality_records_with_missing_binaries.py \
  --cora-url "environment URL" \
  --xml-path "path to source XML files" \
  --fedora-url "Classic Fedora URL"
  --system prod
```