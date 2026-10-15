## CORA-3626

This script replaces a record whose `oldId` is `0` with a new copy, updates incoming links from `diva-output` records, and deletes the original record. Unique constraint values are temporarily removed from the copy and restored after the original has been deleted.

Set `--record-type` and `--old-record-id` to select the record to replace. Use `--record-link-path` to override the XML path used to update links in `diva-output` records; its default is `./data/output/subject/topic/linkedRecordId`.

This script makes changes directly to the selected Cora system. Verify the target and record IDs before running it.

```shell
python src/scripts/one_off/CORA_3626_fix_records_with_id_0.py \
  --cora-url "environment URL" \
  --record-type "someRecordType" \
  --old-record-id "record ID" \
  --system pre \
  --login-id migration@cora.epc.ub.uu.se \ 
  --app-token someToken 
  --record-type diva-organisation 
  --old-record-id 1 
  --record-link-path ./data/output/name/affiliation/organisation/linkedRecordId
```