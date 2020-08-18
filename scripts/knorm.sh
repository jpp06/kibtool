#! /usr/bin/env bash

g_script="$(readlink -f ${BASH_SOURCE[0]})"
g_base="$(dirname ${g_script})"

# options
source ${g_base}/../bash-argsparse-1.8/argsparse.sh
argsparse_use_option outbase     "base filename for storing exported Kibana objects" short:o value mandatory
argsparse_use_option unstringify "unstringify JSON values"                           short:u exclude:stringify
argsparse_use_option stringify   "stringify JSON values"                             short:s exclude:unstringify
argsparse_parse_options "$@"
if ! argsparse_is_option_set unstringify && ! argsparse_is_option_set stringify
then
  printf "One of 'stringify' or 'unstringify' is mandatory\n" >&2
  usage
fi

# let's go
o_outbase="${program_options[outbase]}"
if argsparse_is_option_set unstringify
then
  p_jq_operation=fromjson
fi
if argsparse_is_option_set stringify
then
  p_jq_operation=tojson
fi

g_file=${o_outbase}.dashboard.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${o_outbase}.dashboard.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "dashboard") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_jq_operation}' | .attributes.panelsJSON |= '${p_jq_operation}' | .attributes.optionsJSON |= '${p_jq_operation}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${o_outbase}.visualization.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${o_outbase}.visualization.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "visualization") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_jq_operation}' | .attributes.visState |= '${p_jq_operation}' | .attributes.uiStateJSON |= '${p_jq_operation}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${o_outbase}.search.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${o_outbase}.search.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "search") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_jq_operation}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${o_outbase}.index-pattern.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${o_outbase}.index-pattern.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "index-pattern") | .attributes.fields |= '${p_jq_operation}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${o_outbase}.config.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${o_outbase}.config.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "config") | .attributes | .["visualization:colorMapping"] |= '${p_jq_operation}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

# NYI for timelion-sheet

jq '[ .[] ]' ${o_outbase}.dashboard.json ${o_outbase}.visualization.json ${o_outbase}.search.json ${o_outbase}.index-pattern.json ${o_outbase}.config.json > ${o_outbase}.json
