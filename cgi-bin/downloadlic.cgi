#!/usr/bin/perl -w

$title = "SAL (with Yices) License";

use CGI ':standard';
use CGI::Carp qw(fatalsToBrowser); 

my $file=param('file');

#
# Get list of tar files in the binaries directory
#
opendir(DIR, "binaries") or die "Could not open directory\n\n";
my @list=readdir(DIR);
closedir(DIR);

#
# Check that the requested file is in the list
#
undef $found;
foreach $f (@list) {
    $found = "yes", last if ($f eq $file);
}

unless (defined $found) {
    die "File $file not found\n\n";
}

#
# Prepare the license page
#
print "Content-Type: text/html\n\n";
open(TEMPLATE, "yices-license.template") or die "Could no open template\n\n";

while (<TEMPLATE>) {
    s/____REQUESTED_FILE/$file/g;
    print;
}

close(TEMPLATE);
