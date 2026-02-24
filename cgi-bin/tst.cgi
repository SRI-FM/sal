#!/bin/sh

eval `echo $PREFIX$QUERY_STRING | sed -e 's/'"'"'/%27/g' | \
		      awk 'BEGIN{RS="&";FS="="}
$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
printf "QS_%s=%c%s%c\n",$1,39,$2,39}' `

echo Content-type: text/html
echo ""

/bin/cat << EOM
<html>
<head><title>test</title>
</head>
<p>
HELLO WORLD
<pre>
EOM

echo $QS_result1
echo $QS_result2

cat << EOM
</pre>
</small>
<p>
</body>
</html>
EOM
