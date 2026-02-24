#!/bin/sh

SCRIPT_DIR=/homes/demoura/project/yices/scripts
EXP_DIR=/homes/demoura/project/yices/experiments

# Convert the query string to variables prefixed by QS_
eval `echo $PREFIX$QUERY_STRING | sed -e 's/'"'"'/%27/g' | \
		      awk 'BEGIN{RS="&";FS="="}
$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
printf "QS_%s=%c%s%c\n",$1,39,$2,39}' `

## QS_result1 and QS_result2 contain the results


echo Content-type: text/html
echo ""

(LD_LIBRARY_PATH=""; export LD_LIBRARY_PATH; $SCRIPT_DIR/table.sh $EXP_DIR/$QS_result1 $EXP_DIR/$QS_result2)

