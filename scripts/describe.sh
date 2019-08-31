#! /bin/bash

if [ -z "$1" ]
then
    echo "*** Missing file argument" >&2
    exit 1
fi

# ----------------------------------------------------------------------

cat <<'EOF' > program.jq
def dict(f):
 reduce .[] as $o ({}; .[$o | f | tostring] = $o ) ;

($searchs | .[] | ($index_patterns | dict(.id)) as $pattern_dict | .index = $pattern_dict[.index]) as $searchs_with_index | 
$searchs_with_index | .
EOF

echo '{}' | jq -f program.jq --slurpfile index_patterns $1.pattern --slurpfile searchs $1.search

echo "-----"
cat program.jq

exit 0

# ----------------------------------------------------------------------

echo "--- Extracting dashboard infos from '$1'..."
# "_source" "kibanaSavedObjectMeta" "searchSourceJSON" "filter" "meta" "index"
cat $1 | \
    jq '.[] |
select(._type == "dashboard") | {
  "id": .____id,
  "title": ._source.title,
  "filter_queries": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query? // empty) ],
  "filter_fields": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ],
  "filter_indices": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .index? | strings ],
  "panels": [ ._source.panelsJSON | .. | .id? | strings ],
}' > $1.dash

echo "--- Extracting viz infos from '$1'..."
cat $1 | \
    jq '.[] |
select(._type == "visualization") | {
  "id": .____id,
  "title": ._source.title,
  "index": ._source.kibanaSavedObjectMeta.searchSourceJSON.index,
  "queries": [ ._source.visState | .. | .query? | strings ],
  "filter_queries": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | first(.. | .query?) ],
  "filter_fields": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
}' > $1.viz

echo "--- Extracting search infos from '$1'..."
cat $1 | \
    jq '.[] |
select(._type == "search") | {
  "id": .____id,
  "title": ._source.title,
  "columns": ._source.columns,
  "index": ._source.kibanaSavedObjectMeta.searchSourceJSON.index,
  "filter_queries": [ ._source.kibanaSavedObjectMeta.searchSourceJSON | first(.. | .query?) ],
  "filter_fields": [ ._source.kibanaSavedObjectMeta.searchSourceJSON.filter | .. | .field? | strings ]
}' > $1.search

echo "--- Extracting pattern infos from '$1'..."
cat $1 | \
    jq '.[] |
select(._type == "index-pattern") | {
  "id": .____id,
  "title": ._source.title
}' > $1.pattern
