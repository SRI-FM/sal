#!/csl/bin/perl


$prelude_shtml="smt-comp-prelude.shtml";
$postlude_shtml="smt-comp-postlude.shtml";
# $basedir = "/homes/demoura/public_html/smt-comp";

require "ssi_parse.pl";

# Get the arguments from the QUERY_STRING
$query_string =  $ENV{'QUERY_STRING'};
@values = split(/&/,$query_string);
$dates='all';
$order='normal';
@states=();
foreach $v (@values) {
  ($name,$value) = split(/=/,$v);
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  if ($name eq 'division') {
    $division = $value;
  }
  elsif ($name eq 'system1') {
    $system1 = $value;
  }
  elsif ($name eq 'system2') {
    $system2 = $value;
  }
}

# Start the HTML page
print "Content-type: text/html\n\n";

# Server-side includes are not possible on CGI scripts, so we have to
#   emulate the following
# print "<!--#set var=\"title\" value=\"Title\" -->\n";
# print "<!--#include virtual=\"${prelude_shtml}\" -->\n";
# ssi_parse_and_output($prelude_shtml, 'fh00');

print "<p>Division: $division</p>";
print "<p>System1: $system1</p>";
print "<p>System2: $system2</p>";

# ssi_parse_and_output($postlude_shtml, 'fh00');
print "</body></html>\n";


