#! /usr/bin/env bash

g_script="$(readlink -f ${BASH_SOURCE[0]})"
g_base="$(dirname ${g_script})"

# options
source ${g_base}/../bash-argsparse-1.8/argsparse.sh
argsparse_use_option outbase    "base filename for storing exported Kibana objects" short:o value mandatory
argsparse_use_option esendpoint "Elasticsearch endpoint to connect to"              short:e value mandatory
argsparse_use_option kibspace   "Kibana space where Kibanae object are stored"      short:s value mandatory
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
  rm -f ${o_outbase}.${c_type}.p[0-9]*.json

  l_page=1
  l_count=0
  while
    curl -s -k -u "${USER}:${PASSWORD}" \
         -X GET \
         "${o_url}${l_space_path}/api/saved_objects/_find?type=${c_type}&page=${l_page}" > "${o_outbase}.${c_type}.p${l_page}.json"
    jq . "${o_outbase}.${c_type}.p${l_page}.json" > z ; mv z "${o_outbase}.${c_type}.p${l_page}.json"
    l_count=$(jq ".saved_objects | length" "${o_outbase}.${c_type}.p${l_page}.json")
    [[ ${l_count} != 0 ]]
  do
    l_page=$(( $l_page + 1))
  done

  for f in ${o_outbase}.${c_type}.p[0-9]*.json
  do
    jq '.saved_objects[]' $f
  done | jq -s > ${o_outbase}.${c_type}.json
  rm -f ${o_outbase}.${c_type}.p[0-9]*.json
done

rm -f ${o_outbase}.*.p[0-9]*.json
