#! /usr/bin/env bash

g_script="$(readlink -f ${BASH_SOURCE[0]})"
g_base="$(dirname ${g_script})"

# options
source ${g_base}/../bash-argsparse-1.8/argsparse.sh
argsparse_use_option infile  "name of input file storing exported Kibana objects" short:i value mandatory
argsparse_use_option outfile "name of output file to write (short) description"   short:o value mandatory
argsparse_parse_options "$@"

# let's go
o_infile="${program_options[infile]}"
o_outfile="${program_options[outfile]}"

echo "--- Extracting dashboard infos from '${o_infile}'..."
cat ${o_infile} | \
    jq '[ .[] |
select(.type == "dashboard") | {
  "id": .id,
  "type": "dashboard",
  "title": .attributes.title,
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query? // empty) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ],
  "filter_indices": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .index? | strings ],
  "panels": [ .attributes.panelsJSON | .. | .id? | strings ]
} ]' | jq '.[]' | jq -s '[.[]]' > ${o_infile}.dashboard

echo "--- Extracting viz infos from '${o_infile}'..."
cat ${o_infile} | \
    jq '[ .[] |
select(.type == "visualization") | {
  "id": .id,
  "type": "visualization",
  "title": .attributes.title,
  "index": .attributes.kibanaSavedObjectMeta.searchSourceJSON.index,
  "queries": [ .attributes.visState | .. | .query? | strings ],
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query?) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
} ]' | jq '.[]' | jq -s '[.[]]' > ${o_infile}.visualization

echo "--- Extracting search infos from '${o_infile}'..."
cat ${o_infile} | \
    jq '[ .[] |
select(.type == "search") | {
  "id": .id,
  "type": "search",
  "title": .attributes.title,
  "columns": .attributes.columns,
  "index": .attributes.kibanaSavedObjectMeta.searchSourceJSON.index,
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON | first(.. | .query?) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
} ]' | jq '.[]' | jq -s '[.[]]' > ${o_infile}.search

echo "--- Extracting pattern infos from '${o_infile}'..."
cat ${o_infile} | \
    jq '[ .[] |
select(.type == "index-pattern") | {
  "id": .id,
  "type": "index-pattern",
  "title": .attributes.title
} ]' | jq '.[]' | jq -s '[.[]]' > ${o_infile}.index-pattern

# --------------------------------------------------
echo "--- Merging into '${o_infile}'..."
cat <<'EOF' | python3 - ${o_infile}.dashboard ${o_infile}.visualization ${o_infile}.search ${o_infile}.index-pattern > ${o_outfile}
import json
import sys

def todict(p_filename):
  l_components = {}
  #print(p_filename, file=sys.stderr)
  with open(p_filename, "r") as w_in:
    l_json = json.load(w_in)
    for c_obj in l_json:
      l_components[c_obj["id"]] = c_obj
      del(c_obj["id"])
  return l_components

l_dashboards     = todict(sys.argv[1])
l_visualizations = todict(sys.argv[2])
l_searchs        = todict(sys.argv[3])
l_index_patterns = todict(sys.argv[4])

for c_key, c_val in l_visualizations.items():
  if c_val["index"]:
    c_val["index"] = l_index_patterns[c_val["index"]]["title"]
for c_key, c_val in l_searchs.items():
  if c_val["index"]:
    c_val["index"] = l_index_patterns[c_val["index"]]["title"]
for c_key, c_val in l_dashboards.items():
  l_panels = []
  for c_id in c_val["panels"]:
    if c_id in l_visualizations:
      l_panels.append(l_visualizations[c_id])
    if c_id in l_searchs:
      l_panels.append(l_searchs[c_id])
  c_val["panels"] = l_panels

print(json.dumps(list(l_dashboards.values()), indent=2))
EOF
