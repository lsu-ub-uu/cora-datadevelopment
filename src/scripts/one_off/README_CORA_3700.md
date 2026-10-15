## CORA-3700

This script updates all `diva-output` records that have a subject with `authority="diva"`. It replaces the original subject with one subject per topic, linking each to a `diva-subject` record.

The script updates the selected Cora system directly; it does not provide a dry-run mode. Review the target system before running it.

```shell
python src/scripts/one_off/CORA_3700_update_subject_authority_diva_model.py \
  --cora-url "environment URL"
  --system " 
  --login_id "loginId"
  --app_token "apptoken"
  --cora_url "enviroment url"
```