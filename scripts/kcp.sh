#! /bin/bash

# https://www.elastic.co/guide/en/kibana/master/saved-objects-api.html

[ -z "$1" ] && echo "*** Error: missing base file name argument in command line." >&2 && exit 1
g_out_base=$1

# Config
[ -z "${KT_KIBANA_SRC}" ] && echo "*** Error: missing KT_KIBANA_SRC in environment." >&2 && exit 1
if [[ "${KT_KIBANA_SRC}" =~ "localhost:" ]]
then
  g_creds_src=""
else
  [ -z "${KT_USER_SRC}" ]     && echo "*** Error: missing KT_USER_SRC in environment."     >&2 && exit 1
  [ -z "${KT_PASSWORD_SRC}" ] && echo "*** Error: missing KT_PASSWORD_SRC in environment." >&2 && exit 1
  g_creds_src="-u ${KT_USER_SRC}:${KT_PASSWORD_SRC}"
fi
if [ -z "${KT_SPACE_SRC}" ]
then
  g_space_src=""
else
  g_space_src="/s/${KT_SPACE_SRC}"
fi

# [ -z "${KT_KIBANA_DST}" ] && echo "*** Error: missing KT_KIBANA_DST in environment." >&2 && exit 1
# if [[ "${KT_KIBANA_DST}" =~ "localhost:" ]]
# then
#   g_creds_dst=""
# else
#   [ -z "${KT_USER_DST}" ]     && echo "*** Error: missing KT_USER_DST in environment."     >&2 && exit 1
#   [ -z "${KT_PASSWORD_DST}" ] && echo "*** Error: missing KT_PASSWORD_DST in environment." >&2 && exit 1
#   g_creds_dst="-u ${KT_USER_DST}:${KT_PASSWORD_DST}"
# fi
# if [ -z "${KT_SPACE_DST}" ]
# then
#   g_space_dst=""
# else
#   g_space_dst="/s/${KT_SPACE_DST}"
# fi

# Let's go
g_k_src=${KT_KIBANA_SRC}
g_fields='&fields=id&fields=type'
for c_type in config dashboard index-pattern search timelion-sheet visualization
do
  rm -f ${g_out_base}.${c_type}.p[0-9]*.json

  l_page=1
  l_count=0
  while
    curl -s -k "${g_creds_src}" \
         -X GET \
         "${g_k_src}${g_space_src}/api/saved_objects/_find?search=*&type=${c_type}&page=${l_page}${g_fields}" > "${g_out_base}.${c_type}.p${l_page}.json"
    l_count=$(jq ".saved_objects | length" "${g_out_base}.${c_type}.p${l_page}.json")

    [[ ${l_count} != 0 && -s ${g_out_base}.${c_type}.p${l_page}.json ]]
  do
    l_page=$(( $l_page + 1))
  done
done

jq -s -c ".[].saved_objects[] | { id: .id, type: .type }" ${g_out_base}.*.json

#rm -f ${g_out_base}.*.p[0-9]*.json
