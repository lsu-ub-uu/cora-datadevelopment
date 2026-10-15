## CORA-3835
This script will update binaries with a `<status>done</status>` for each binary that doesn't already have have a status.

With the `cora-url` parameter you select the enviroment to update the posts at. 


```shell
python src/scripts/one_off/CORA_3835_update_binaries_with_status \
  --cora-url "enviroment url"
```