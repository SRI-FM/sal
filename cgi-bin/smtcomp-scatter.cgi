#!/bin/sh

SCRIPT_DIR=/homes/demoura/smtcomp/scripts

# Convert the query string to variables prefixed by QS_
eval `echo $PREFIX$QUERY_STRING | sed -e 's/'"'"'/%27/g' | sed -e 's/%2F/\//g' | \
		      awk 'BEGIN{RS="&";FS="="}
$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
printf "QS_%s=%c%s%c\n",$1,39,$2,39}' `

## QS_result1 and QS_result2 contain the results

echo Content-type: image/png
echo ""

$SCRIPT_DIR/scatter.sh $QS_result1 $QS_result2

