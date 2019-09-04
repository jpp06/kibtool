#! /bin/bash

if [ -z "$1" ]
then
    echo "*** Missing file argument" >&2
    exit 1
fi

# ----------------------------------------------------------------------

echo "--- Extracting dashboard infos from '$1'..."
# "_source" "kibanaSavedObjectMeta" "searchSourceJSON" "filter" "meta" "index"
cat $1 | \
    jq '[ .[] |
select(.type == "dashboard") | {
  "id": .id,
  "type": "dashboard",
  "title": .attributes.title,
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query? // empty) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ],
  "filter_indices": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .index? | strings ],
  "panels": [ .attributes.panelsJSON | .. | .id? | strings ],
} ]' > $1.dashboard

echo "--- Extracting viz infos from '$1'..."
cat $1 | \
    jq '[ .[] |
select(.type == "visualization") | {
  "id": .id,
  "type": "visualization",
  "title": .attributes.title,
  "index": .attributes.kibanaSavedObjectMeta.searchSourceJSON.index,
  "queries": [ .attributes.visState | .. | .query? | strings ],
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query?) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
} ]' > $1.visualization

echo "--- Extracting search infos from '$1'..."
cat $1 | \
    jq '[ .[] |
select(.type == "search") | {
  "id": .id,
  "type": "search",
  "title": .attributes.title,
  "columns": .attributes.columns,
  "index": .attributes.kibanaSavedObjectMeta.searchSourceJSON.index,
  "filter_queries": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON | first(.. | .query?) ],
  "filter_fields": [ .attributes.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
} ]' > $1.search

echo "--- Extracting pattern infos from '$1'..."
cat $1 | \
    jq '[ .[] |
select(.type == "index-pattern") | {
  "id": .id,
  "type": "index-pattern",
  "title": .attributes.title
} ]' > $1.index-pattern

# --------------------------------------------------
cat <<'EOF' | python3 - $1.dashboard $1.visualization $1.search $1.index-pattern > z.json
import json
import sys

def todict(p_filename):
  l_components = {}
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

exit

------------------------------
def dict(f):
  reduce .[] as $o ({}; .[$o | f | tostring] = $o ) ;

def dict_dash:
  reduce .[] as $o ({}; { id: ($o | .id), value: ($o | .panels) } ) ;

def replz(p; $d):
  p | .[] | . |= $d[.id] ;

($index_patterns | dict(.id)) as $pattern_dict |
($visualizations | .[] | select(.index != null) | .index = $pattern_dict[.index]) as $vizs_with_index |
([ $vizs_with_index ] | dict(.id)) as $viz_dict |
($searchs | .[] | .index = $pattern_dict[.index]) as $searchs_with_index |
([ $searchs_with_index ] | dict(.id)) as $search_dict |
[ $search_dict, $viz_dict ] | .[] as $component_dict |
$dashboards | .[]
EOF


exit

