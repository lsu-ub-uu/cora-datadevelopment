## CORA-3762

This script migrates personal-name role terms that have a `repeatId` in `diva-output` records into separate `role` groups, preserving each term's repeat ID.

By default, the script runs in dry-run mode and logs the changes it would make. Add `--apply` to write the updates to the selected Cora system.

To apply the changes, add `--apply` to the command.

```shell
python src/scripts/one_off/CORA_3762_update_roles.py \
  --cora-url "environment URL"
```
