# PERL script for generating GNATS reports
# assumes the following are set by the script that requires this one:
#  $prelude_shtml, e.g., pvs-prelude.shtml
#  $postlude_shtml, e.g., pvs-postlude.shtml
#  $gnatsdb, e.g., "/csl/mail/gnats/pvs"
#  $list_cgi, e.g., pvs-bug-list
#  $report_cgi, e.g., pvs-bug

require "ssi_parse.pl";

# Get the arguments from the QUERY_STRING

$query_string =  $ENV{'QUERY_STRING'};
($fieldname,$id) = split(/=/,$query_string);

%ssi_var_map = (title => "$system Bug $id");

print "Content-type: text/html\n\n";
ssi_parse_and_output($prelude_shtml, 'fh00');

open(FILE,"$gnatsdb/$id") || die "Can't open $gnatsdb/$file\n";

print "<hr /><pre>\n";

while (<FILE>) {
  s/\n$//;
  if (/^>Audit-Trail:/) {
    $printing=0;
  }
  elsif (/^>Category:/) {
    $printing=1;
  }
  elsif (/^>Confidential:/ || /^>Submitter-Id:/) {
  }
  elsif ($printing && /^>Organization:$/) {
    print "<font color=red>Organization:</font>    ";
  }
  elsif ($printing && /^>([^:]*:)(.*)$/) {
    print "<font color=red>$1</font> $2\n";
  }
  elsif ($printing) {
    s/&/&amp;/g; s/</&lt;/g; s/>/&gt;/g;
    print "$_\n";
  }
}
print "</pre>";

ssi_parse_and_output($postlude_shtml, 'fh00');

print "</html>";
