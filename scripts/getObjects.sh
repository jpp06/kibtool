#! /bin/bash

if [ -z "$1" ]
then
    echo "*** Missing url [and space]" >&2
    exit 1
fi

o_url=$1
o_space=$2

g_out_base=./toto

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
  rm -f ${g_out_base}.${c_type}.p[0-9]*.json

  l_page=1
  l_count=0
  while
    curl -s -k -u "${USER}:${PASSWORD}" \
         -X GET \
         "${o_url}${l_space_path}/api/saved_objects/_find?type=${c_type}&page=${l_page}" > "${g_out_base}.${c_type}.p${l_page}.json"
    jq . "${g_out_base}.${c_type}.p${l_page}.json" > z ; mv z "${g_out_base}.${c_type}.p${l_page}.json"
    l_count=$(jq ".saved_objects | length" "${g_out_base}.${c_type}.p${l_page}.json")
    [[ ${l_count} != 0 ]]
  do
    l_page=$(( $l_page + 1))
  done

  for f in ${g_out_base}.${c_type}.p[0-9]*.json
  do
    jq '.saved_objects[]' $f
  done | jq -s > ${g_out_base}.${c_type}.json
  rm -f ${g_out_base}.${c_type}.p[0-9]*.json
done

rm -f ${g_out_base}.*.p[0-9]*.json
