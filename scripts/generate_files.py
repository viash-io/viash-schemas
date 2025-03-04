import json
import os

versions_url = "https://viash.io/versions.json"

# download versions in tempfile
versions = json.loads(os.popen(f"curl -s {versions_url}").read())

# for each version
for version_dict in versions["versions"]:
  version = version_dict.get("version")

  if not version:
    # old version.json format
    link = version_dict.get("link")
    if link == "":
      link = versions["latest"]
    
    version = link.replace("_", ".")

  # skip 0.7.4 because it doesn't support the export json_schema command
  if version == "0.7.4":
    continue

  # prep dir
  dir = f"json_schemas/{version}"

  if not os.path.exists(dir):
    os.makedirs(dir)
  
  # generate config schema if it doesn't exist
  config_schema_path = f"{dir}/config.schema.json"
  if not os.path.exists(config_schema_path):
    print(f"Generating schema for version {version}")
    os.system(f"VIASH_VERSION={version} viash export json_schema --format json --output {config_schema_path}")
  
  # generate package schema if it doesn't exist
  package_schema = f"""\
  {{
    "$schema" : "http://json-schema.org/draft-07/schema#",
    "$ref": "https://raw.githubusercontent.com/viash-io/viash-schemas/refs/heads/main/{config_schema_path}#/definitions/PackageConfig"
  }}
  """
  package_schema_path = f"{dir}/package.schema.json"
  if not os.path.exists(package_schema_path):
    print(f"Generating package schema for version {version}")
    with open(package_schema_path, "w") as f:
      f.write(package_schema)
