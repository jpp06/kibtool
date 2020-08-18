#! /usr/bin/env bash

g_script="$(readlink -f ${BASH_SOURCE[0]})"
g_base="$(dirname ${g_script})"

# options
source ${g_base}/../bash-argsparse-1.8/argsparse.sh
argsparse_use_option inbase     "base filename of exported Kibana objects"     short:i value mandatory
argsparse_use_option esendpoint "Elasticsearch endpoint to connect to"         short:e value mandatory
argsparse_use_option kibspace   "Kibana space where Kibanae object are stored" short:s value mandatory
argsparse_parse_options "$@"

# let's go
o_url="${program_options[esendpoint]}"
o_space="${program_options[kibspace]}"
o_inbase="${program_options[inbase]}"

if [ -z "${o_space}" ]
then
  l_space_path=""
else
  l_space_path="/s/${o_space}"
fi

if [ -z "$PASSWORD" ]
then
  echo -n "Password for '${USER}': "
  read -s PASSWORD
  echo
fi

echo "--- ${o_inbase}"
grep -v updated_at ${o_inbase}.json > z.json
curl -s -k -u "${USER}:${PASSWORD}" \
     -X POST -H 'kbn-xsrf: true' -H 'Content-Type: application/json' --data-binary @"z.json" \
     "${o_url}${l_space_path}/api/saved_objects/_bulk_create" | jq .
echo
