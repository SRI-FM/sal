# PERL script for generating GNATS listings
# assumes the following are set by the script that requires this one:
#  $prelude_shtml, e.g., pvs-prelude.shtml
#  $postlude_shtml, e.g., pvs-postlude.shtml
#  $gnatsdb, e.g., "/csl/mail/gnats/pvs"
#  $list_cgi, e.g., pvs-bug-list
#  $report_cgi, e.g., pvs-bug

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
  if ($name eq 'dates') {
    $dates = $value;
  }
  elsif ($name eq 'order') {
    $order = $value;
  }
  elsif ($name eq 'search') {
    $search_regexp = $value;
  }
  elsif ($name eq 'originator') {
    $originator_regexp = $value;
  }
  elsif ($name eq 'status') {
    push(@states,$value);
  }
}
$reversep=($order eq 'reverse');
if (! @states) {
  push(@states,'open');
  push(@states,'analyzed');
}

@event_keys=$reversep ? sort numerically keys(%events) : sort numreverse keys(%events);
%ssi_var_map = ();

# Start the HTML page
print "Content-type: text/html\n\n";

# Server-side includes are not possible on CGI scripts, so we have to
#   emulate the following
# print "<!--#set var=\"title\" value=\"Title\" -->\n";
# print "<!--#include virtual=\"${prelude_shtml}\" -->\n";
ssi_parse_and_output($prelude_shtml, 'fh00');

# Start of form
print "<hr><p><form action=\"$list_cgi\">\n";
print "<input type=submit value=\"search\"> based on the information below:<p>";
# The search button
print "<p>Search (regexp) <input type=text name=search value=\"", $search_regexp, "\">&nbsp;&nbsp;\n";
# The Originator button
print "Submitted by (regexp) <input type=text name=originator value=\"", $originator_regexp, "\"></p><p>\n";
# State checkboxes
$checked = ""; foreach $s (@states) { $checked = "checked" if ($s eq 'open') };
print "<input type=\"checkbox\" $checked name=\"status\" value=\"open\">&nbsp;<b>open</b>: ";
print "The problem has been filed and the responsible person notified<br>\n";
$checked = ""; foreach $s (@states) { $checked = "checked" if ($s eq 'analyzed') };
print "<input type=checkbox $checked name=status value=\"analyzed\">&nbsp;<b>analyzed</b>: ";
print "The problem has been resolved internally at SRI<br>\n";
$checked = ""; foreach $s (@states) { $checked = "checked" if ($s eq 'feedback') };
print "<input type=checkbox $checked name=status value=\"feedback\">&nbsp;<b>feedback</b>: ";
print "The problem has been resolved, and any changes are in the latest release<br>\n";
$checked = ""; foreach $s (@states) { $checked = "checked" if ($s eq 'closed') };
print "<input type=checkbox $checked name=status value=\"closed\">&nbsp;<b>closed</b>: ";
print "The problem has been resolved, and any changes are in an earlier release<br>\n";
$checked = ""; foreach $s (@states) { $checked = "checked" if ($s eq 'suspended')};
print "<input type=checkbox $checked name=status value=\"suspended\">&nbsp;<b>suspended</b>: ";
print "Work on the problem has been postponed, usually because it can't be recreated\n";
# The Submitted since button
print "<p>Submitted since <select name=dates>\n";
print "<option ", ($dates eq 'all' ? "selected " : ""), "value=all>ever\n";
print "<option ", ($dates eq '365' ? "selected " : ""), "value=365>last year\n";
print "<option ", ($dates eq '181' ? "selected " : ""), "value=183>last 6 months\n";
print "<option ", ($dates eq '122' ? "selected " : ""), "value=122>last 4 months\n";
print "<option ", ($dates eq '61' ? "selected " : ""), "value=61>last 2 months\n";
print "<option ", ($dates eq '31' ? "selected " : ""), "value=31>last month\n";
print "<option ", ($dates eq '14' ? "selected " : ""), "value=14>last 2 weeks\n";
print "<option ", ($dates eq '7' ? "selected " : ""), "value=7>last week\n";
print "<option ", ($dates eq '2' ? "selected " : ""), "value=2>last 2 days\n";
print "<option ", ($dates eq '1' ? "selected " : ""), "value=1>yesterday\n";
print "</select>\n";
print "in <select name=order>";
print "<option ", ($reversep ? "selected " : ""), "value=reverse>reverse\n";
print "<option ", ($reversep ? "" : "selected "), "value=normal>normal\n";
print "</select>\n chronological order.\n";
print "</form><hr>\n";
# End of form
print "<p>";

print "Note: this makes use of the GNATS bug tracking system available at ";
print "<a href=\"ftp://prep.ai.mit.edu/pub/gnu/\">";
print "ftp://prep.ai.mit.edu/pub/gnu/</a>. The report numbers have gaps ";
print "because of tests and the way the GNATs system works.";
print "<p>";

if (! opendir(DBDIR,$gnatsdb)) {
    print "Can't open database directory $gnatsdb\n";
    exit(0);
}

print "<table border=1 cellspacing=0 cellpadding=3>\n";
print "<tr align=center valign=center>\n";
print "<th align=right>No.</th>\n";
print "<th>Status</th>\n";
print "<th>Date</th>\n";
print "<th align=left>Submitted by</th>\n";
print "<th align=left>Synopsis</th>\n";
print "</tr>\n";

sub numerically { $a <=> $b };
sub numreverse { $b <=> $a };
@dbfiles = $reversep ? sort numreverse readdir(DBDIR) : sort numerically readdir(DBDIR);
foreach $file (@dbfiles) {
  if ($file =~ /^\d*$/) {
    open(FILE,"$gnatsdb/$file") || die "Can't open $gnatsdb/$file\n";
    $search_match=($search_regexp eq '');
    while (<FILE>) {
      s/\n$//;
      if (/^>Number:\s*(.*)$/) {
	$number=$1;
      }
      elsif (/^>Synopsis:\s*(.*)$/) {
	$synopsis=$1;
      }
      elsif (/^>State:\s*(.*)$/) {
	$state=$1;
      }
      elsif (/^>Arrival-Date:\s*(.*)/) {
	$date=&fix_date($1);
      }
      elsif (/^>Originator:\s*(.*)/) {
	$originator=$1;
      }
      elsif (!$search_match) {
	$search_match = m!${search_regexp}!i;
      }
    }
    $state_match = 0;
    foreach $s (@states) {
      $state_match = 1 if ($state eq $s)
	&& ($dates eq 'all' || &within_date($date, $dates))
	&& ($originator_regexp eq '' || $originator =~ /$originator_regexp/i)
	&& ($search_match);
    }
    if (@event_keys &&
	((!$reversep && $file > @event_keys[$#event_keys]) ||
	 ($reversep && $file <= @event_keys[$#event_keys]))) {
      print "<tr align=left><td colspan=5><font color=red>$events{@event_keys[$#event_keys]}</font></td>\n";
      pop(@event_keys);
    }
    if ($state_match) {
      printf "<tr>";
      printf "<td align=right><a href=\"../$report_cgi?id=$number\">$number</a></td>";
      printf "<td align=center>$state</td>";
      printf "<td align=center nowrap>$date</td>";
      $originator =~ s/\"//g; 
      printf "<td align=left>$originator</td>";
      printf "<td align=left>$synopsis</td>";
      printf "</tr>\n";
    }
  }
}
while (@event_keys) {
  print "<tr align=left><td colspan=5><font color=red>$events{@event_keys[$#event_keys]}</font></td>\n";
  pop(@event_keys);
}
print "</table>\n";
print "<p />\n";
# Server-side includes are not possible on CGI scripts, so we have to
#   emulate the following
# print "<!--#include virtual=\"navbar.shtml\" -->\n";
ssi_parse_and_output($postlude_shtml, 'fh00');
print "</body></html>\n";


sub fix_date {
  %months=('Jan', '01', 'Feb', '02', 'Mar', '03', 'Apr', '04', 'May', '05',
	   'Jun', '06', 'Jul', '07', 'Aug', '08', 'Sep', '09', 'Oct', '10',
	   'Nov', '11', 'Dec', '12');
  local ($day,$mon,$date,$time,$offset,$year) = split(' ',@_[0]);
  if (! $year) {$year = $offset};
  join('-',$year,$months{$mon},sprintf('%.2d',$date));
}

sub within_date {
  if (@_[0] eq 'all') {
    1;
  } else {
    local ($byear,$bmonth,$bday) = split('-',@_[0]);
    local @ltime = localtime(time);
    local ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = @ltime;
    local $ydiff = ($year + 1900 - $byear) * 365.25;
    local $mdiff = ($mon + 1 - $bmonth) * 30.4;
    local $ddiff = $mday - $bday + $mdiff + $ydiff;
    return $ddiff  < @_[1];
  }
}
