#!/bin/sh

SCRIPT_DIR=/homes/demoura/project/yices/scripts
EXP_DIR=/homes/demoura/project/yices/experiments

# Convert the query string to variables prefixed by QS_
eval `echo $PREFIX$QUERY_STRING | sed -e 's/'"'"'/%27/g' | \
		      awk 'BEGIN{RS="&";FS="="}
$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
printf "QS_%s=%c%s%c\n",$1,39,$2,39}' `

## QS_result1 and QS_result2 contain the results

f1=/tmp/f1$$.txt
f2=/tmp/f2$$.txt
f3=/tmp/f3$$.txt
$SCRIPT_DIR/time.sh $EXP_DIR/$QS_result1 > $f1
$SCRIPT_DIR/time.sh $EXP_DIR/$QS_result2 > $f2
(LD_LIBRARY_PATH=""; export LD_LIBRARY_PATH; $SCRIPT_DIR/join.sh $f1 $f2) > $f3

echo Content-type: text/html
echo ""

cat <<EOF
<html>
<head>
<title>Runtime comparison: $QS_result1 and $QS_result2</title>
</head>
<body bgcolor="#ffffff">
<h1>Runtime comparison: $QS_result1 and $QS_result2</h1>
EOF

$SCRIPT_DIR/to_html_table.sh $f3

cat <<EOF
</body>
</html>
EOF

rm -f $f1
rm -f $f2
rm -f $f3


