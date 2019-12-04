#! /usr/bin/env bash

g_script="$(readlink -f ${BASH_SOURCE[0]})"
g_base="$(dirname ${g_script})"

# options
source ${g_base}/../bash-argsparse-1.8/argsparse.sh
argsparse_use_option outbase    "base filename for storing exported Kibana objects" short:o value mandatory
argsparse_use_option esendpoint "Elasticsearch endpoint to connect to"              short:e value mandatory
argsparse_use_option kibspace   "Kibana space where Kibana object are stored"       short:s value mandatory
argsparse_parse_options "$@"

# let's go
o_url="${program_options[esendpoint]}"
o_space="${program_options[kibspace]}"
o_outbase="${program_options[outbase]}"

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

for c_type in visualization dashboard search index-pattern config timelion-sheet
do
  curl -s -k -u "${USER}:${PASSWORD}" -H "kbn-xsrf: reporting" \
       -X POST \
       "${o_url}${l_space_path}/api/saved_objects/_export" -d '
{
  "type": "'${c_type}'"
}
' > "${o_outbase}.${c_type}.ndjson"
done
