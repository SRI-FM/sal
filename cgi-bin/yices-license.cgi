#!/usr/bin/perl -w

read (STDIN, $query_string, $ENV{'CONTENT_LENGTH'});

@key_value_pairs = split (/&/, $query_string);

print "Content-type: text/html", "\n\n";
print "<html>", "\n";
print "<body>", "\n";

if ($#key_value_pairs == 0) {
    ($key, $value) = split (/=/, @key_value_pairs[0]);
    $value =~ tr/+/ /;
    if ($key eq "accept") {
	print "Thank you for accepting the license\n";
    } elsif ($key eq "reject") {
	print "Please contact us Yices\n";
	print "If  accepting the license\n";
    } else {
	print "Error: bad request", "\n";
    }
}
else {
    print "Error: bad request", "\n";
}

print "<br>", "\n";
print "</body>", "\n";
print "</html>", "\n";
