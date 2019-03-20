#!/bin/sh
curl "https://www.wikidata.org/w/api.php?action=compare&fromrev=$1&torev=$2&format=json&uselang=en" | jq -r  ".compare[\"*\"]"
