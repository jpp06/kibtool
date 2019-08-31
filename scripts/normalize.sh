#! /bin/bash

if [ -z "$1" ]
then
    echo "*** Missing basename" >&2
    exit 1
fi

p_base=$1
p_what=fromjson

g_file=${p_base}.dashboard.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${p_base}.dashboard.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "dashboard") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_what}' | .attributes.panelsJSON |= '${p_what}' | .attributes.optionsJSON |= '${p_what}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${p_base}.visualization.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${p_base}.visualization.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "visualization") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_what}' | .attributes.visState |= '${p_what}' | .attributes.uiStateJSON |= '${p_what}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${p_base}.search.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${p_base}.search.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "search") | .attributes.kibanaSavedObjectMeta.searchSourceJSON |= '${p_what}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${p_base}.index-pattern.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${p_base}.index-pattern.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "index-pattern") | .attributes.fields |= '${p_what}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

g_file=${p_base}.config.json
echo "--- Normalizing '${g_file}'..."
g_temp=$(mktemp)
mv ${p_base}.config.json ${g_temp}
cat ${g_temp} | sed -e 's/  "_id":/  "____id":/' | jq --indent 0 '.[]' | sort | \
    jq -s -S '[ .[] |
( select(.type == "config") | .attributes | .["visualization:colorMapping"] |= '${p_what}' | . )
]' | \
    sed -e 's/  "____id":/  "_id":/' > ${g_file}

# NYI for timelion-sheet
